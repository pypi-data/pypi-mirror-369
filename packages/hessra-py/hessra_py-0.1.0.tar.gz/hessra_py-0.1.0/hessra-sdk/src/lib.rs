//! # Hessra SDK
//!
//! A Rust client library for interacting with Hessra authentication services.
//!
//! The Hessra SDK provides a robust and flexible way to request and verify authentication tokens
//! for protected resources using mutual TLS (mTLS) for secure client authentication.
//!
//! This crate combines functionality from:
//! - `hessra-token`: Token verification and attestation
//! - `hessra-config`: Configuration management
//! - `hessra-api`: HTTP client for the Hessra service
//!
//! ## Features
//!
//! - **Flexible configuration**: Load configuration from various sources (environment variables, files, etc.)
//! - **Protocol support**: HTTP/1.1 support with optional HTTP/3 via feature flag
//! - **Mutual TLS**: Strong security with client and server certificate validation
//! - **Token management**: Request and verify authorization tokens
//! - **Local verification**: Retrieve and store public keys for local token verification
//! - **Service chains**: Support for service chain attestation and verification
//!
//! ## Feature Flags
//!
//! - `http3`: Enables HTTP/3 protocol support
//! - `toml`: Enables configuration loading from TOML files
//! - `wasm`: Enables WebAssembly support for token verification

use std::fs::File;
use std::io::Read;
use std::path::Path;
use thiserror::Error;

// Re-export everything from the component crates
pub use hessra_token::{
    // Token attestation
    add_service_node_attestation,
    decode_token,
    encode_token,
    // Token verification
    verify_biscuit_local,
    verify_service_chain_biscuit_local,
    // Re-exported biscuit types
    Biscuit,
    KeyPair,
    PublicKey,
    // Service chain types
    ServiceNode,
    // Token errors
    TokenError,
};

pub use hessra_config::{ConfigError, HessraConfig, Protocol};

pub use hessra_api::{
    ApiError, HessraClient, HessraClientBuilder, PublicKeyResponse, SignTokenRequest,
    SignTokenResponse, SignoffInfo, TokenRequest, TokenResponse, VerifyServiceChainTokenRequest,
    VerifyTokenRequest, VerifyTokenResponse,
};

/// Errors that can occur in the Hessra SDK
#[derive(Error, Debug)]
pub enum SdkError {
    /// Configuration error
    #[error("Configuration error: {0}")]
    Config(#[from] ConfigError),

    /// API error
    #[error("API error: {0}")]
    Api(#[from] ApiError),

    /// Token error
    #[error("Token error: {0}")]
    Token(#[from] TokenError),

    /// JSON serialization error
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    /// I/O error
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    /// Generic error
    #[error("{0}")]
    Generic(String),
}

/// A chain of service nodes
///
/// Represents an ordered sequence of service nodes that form a processing chain.
/// The order of nodes in the chain is significant - it defines the expected
/// order of processing and attestation.
#[derive(Clone, Debug, Default)]
pub struct ServiceChain {
    /// The nodes in the chain, in order
    nodes: Vec<ServiceNode>,
}

impl ServiceChain {
    /// Create a new empty service chain
    pub fn new() -> Self {
        Self { nodes: Vec::new() }
    }

    /// Create a service chain with the given nodes
    pub fn with_nodes(nodes: Vec<ServiceNode>) -> Self {
        Self { nodes }
    }

    /// Create a new service chain builder
    pub fn builder() -> ServiceChainBuilder {
        ServiceChainBuilder::new()
    }

    /// Add a node to the chain
    pub fn add_node(&mut self, node: ServiceNode) -> &mut Self {
        self.nodes.push(node);
        self
    }

    /// Add a node to the chain (builder style)
    pub fn with_node(mut self, node: ServiceNode) -> Self {
        self.nodes.push(node);
        self
    }

    /// Get the nodes in the chain
    pub fn nodes(&self) -> &[ServiceNode] {
        &self.nodes
    }

    /// Convert to internal representation for token verification
    fn to_internal(&self) -> Vec<hessra_token::ServiceNode> {
        self.nodes.to_vec()
    }

    /// Load a service chain from a JSON string
    pub fn from_json(json: &str) -> Result<Self, SdkError> {
        let nodes: Vec<ServiceNode> = serde_json::from_str(json)?;
        Ok(Self::with_nodes(nodes))
    }

    /// Load a service chain from a JSON file
    pub fn from_json_file(path: impl AsRef<Path>) -> Result<Self, SdkError> {
        let mut file = File::open(path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        Self::from_json(&contents)
    }

    /// Load a service chain from a TOML string
    #[cfg(feature = "toml")]
    pub fn from_toml(toml_str: &str) -> Result<Self, SdkError> {
        use serde::Deserialize;

        #[derive(Deserialize)]
        struct TomlServiceChain {
            nodes: Vec<ServiceNode>,
        }

        let chain: TomlServiceChain = toml::from_str(toml_str)
            .map_err(|e| SdkError::Generic(format!("TOML parse error: {e}")))?;

        Ok(Self::with_nodes(chain.nodes))
    }

    /// Load a service chain from a TOML file
    #[cfg(feature = "toml")]
    pub fn from_toml_file(path: impl AsRef<Path>) -> Result<Self, SdkError> {
        let mut file = File::open(path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        Self::from_toml(&contents)
    }
}

/// Builder for a service chain
#[derive(Debug, Default)]
pub struct ServiceChainBuilder {
    nodes: Vec<ServiceNode>,
}

impl ServiceChainBuilder {
    /// Create a new service chain builder
    pub fn new() -> Self {
        Self::default()
    }

    /// Add a node to the chain
    pub fn add_node(mut self, node: ServiceNode) -> Self {
        self.nodes.push(node);
        self
    }

    /// Build the service chain
    pub fn build(self) -> ServiceChain {
        ServiceChain::with_nodes(self.nodes)
    }
}

/// Unified SDK for Hessra authentication services
///
/// This struct provides a high-level interface combining functionality
/// from all component crates (config, token, api).
pub struct Hessra {
    client: HessraClient,
    config: HessraConfig,
}

impl Hessra {
    /// Create a new Hessra SDK instance from a configuration
    pub fn new(config: HessraConfig) -> Result<Self, SdkError> {
        let client = HessraClientBuilder::new()
            .from_config(&config)
            .build()
            .map_err(|e| SdkError::Generic(e.to_string()))?;

        Ok(Self { client, config })
    }

    /// Create a builder for a Hessra SDK instance
    pub fn builder() -> HessraBuilder {
        HessraBuilder::new()
    }

    /// Setup the SDK with the public key
    ///
    /// This will fetch the public key from the Hessra service and set it in the SDK configuration.
    /// If the public key is already set, it will be overwritten.
    /// Requires a mutable reference to the SDK instance.
    pub async fn setup(&mut self) -> Result<(), SdkError> {
        match self.get_public_key().await {
            Ok(public_key) => {
                self.config.public_key = Some(public_key);
                Ok(())
            }
            Err(e) => Err(SdkError::Generic(e.to_string())),
        }
    }

    /// Setup the SDK with the public key and return a new instance
    ///
    /// This will fetch the public key from the Hessra service and set it in the SDK configuration.
    /// If the public key is already set, it will be overwritten.
    pub async fn with_setup(&self) -> Result<Self, SdkError> {
        match self.get_public_key().await {
            Ok(public_key) => {
                let config = self.config.to_builder().public_key(public_key).build()?;
                Ok(Self::new(config)?)
            }
            Err(e) => Err(SdkError::Generic(e.to_string())),
        }
    }

    /// Request a token for a resource
    /// Returns the full TokenResponse which may include pending signoffs for multi-party tokens
    pub async fn request_token(
        &self,
        resource: impl Into<String>,
        operation: impl Into<String>,
    ) -> Result<TokenResponse, SdkError> {
        self.client
            .request_token(resource.into(), operation.into())
            .await
            .map_err(|e| SdkError::Generic(e.to_string()))
    }

    /// Request a token for a resource (simple version)
    /// Returns just the token string for backward compatibility
    pub async fn request_token_simple(
        &self,
        resource: impl Into<String>,
        operation: impl Into<String>,
    ) -> Result<String, SdkError> {
        let response = self.request_token(resource, operation).await?;
        match response.token {
            Some(token) => Ok(token),
            None => Err(SdkError::Generic(format!(
                "Failed to get token: {}",
                response.response_msg
            ))),
        }
    }

    /// Sign a multi-party token by calling an authorization service's signoff endpoint
    pub async fn sign_token(
        &self,
        token: &str,
        resource: &str,
        operation: &str,
    ) -> Result<SignTokenResponse, SdkError> {
        self.client
            .sign_token(token, resource, operation)
            .await
            .map_err(|e| SdkError::Generic(e.to_string()))
    }

    /// Parse an authorization service URL to extract base URL and port
    /// Handles URLs like "https://hostname:port/path" or "hostname:port/path"
    /// Returns (base_url, port) where base_url is just the hostname part
    fn parse_authorization_service_url(url: &str) -> Result<(String, Option<u16>), SdkError> {
        let url_str = if url.starts_with("http://") || url.starts_with("https://") {
            url.to_string()
        } else {
            // If no protocol, assume https for parsing
            format!("https://{url}")
        };

        let parsed_url = url::Url::parse(&url_str).map_err(|e| {
            SdkError::Generic(format!(
                "Failed to parse authorization service URL '{url}': {e}"
            ))
        })?;

        let host = parsed_url
            .host_str()
            .ok_or_else(|| SdkError::Generic(format!("No host found in URL: {url}")))?;

        // For URLs where port is not explicitly specified but the scheme indicates a default port,
        // we need to check if the original URL had an explicit port
        let port = if parsed_url.port().is_some() {
            parsed_url.port()
        } else if url.contains(':') && !url.starts_with("http://") && !url.starts_with("https://") {
            // If the original URL has a colon and no protocol, it likely has an explicit port
            // Try to extract it manually
            if let Some(host_port) = url.split('/').next() {
                if let Some(port_str) = host_port.split(':').nth(1) {
                    port_str.parse::<u16>().ok()
                } else {
                    None
                }
            } else {
                None
            }
        } else {
            parsed_url.port()
        };

        Ok((host.to_string(), port))
    }

    /// Collect all required signoffs for a multi-party token
    /// Returns the fully signed token once all signoffs are collected
    pub async fn collect_signoffs(
        &self,
        initial_token_response: TokenResponse,
        resource: &str,
        operation: &str,
    ) -> Result<String, SdkError> {
        // If no pending signoffs, return the token immediately
        let pending_signoffs = match &initial_token_response.pending_signoffs {
            Some(signoffs) if !signoffs.is_empty() => signoffs,
            _ => {
                return initial_token_response
                    .token
                    .ok_or_else(|| SdkError::Generic("No token in response".to_string()))
            }
        };

        let mut current_token = initial_token_response.token.ok_or_else(|| {
            SdkError::Generic("No initial token to collect signoffs for".to_string())
        })?;

        // For each SignoffInfo in pending_signoffs, create a client and call sign_token
        for signoff_info in pending_signoffs {
            // Parse the authorization service URL to extract base URL and port
            let (base_url, port) =
                Self::parse_authorization_service_url(&signoff_info.authorization_service)?;

            // Create a temporary client for this authorization service
            // Note: This is a simplified approach. In practice, you might want to
            // have a configuration system for managing multiple service certificates
            let mut client_builder = HessraClientBuilder::new()
                .base_url(base_url)
                .protocol(self.config.protocol.clone())
                .mtls_cert(self.config.mtls_cert.clone())
                .mtls_key(self.config.mtls_key.clone())
                .server_ca(self.config.server_ca.clone());

            if let Some(port) = port {
                client_builder = client_builder.port(port);
            }

            let signoff_client = client_builder
                .build()
                .map_err(|e| SdkError::Generic(format!("Failed to create signoff client: {e}")))?;

            let sign_response = signoff_client
                .sign_token(&current_token, resource, operation)
                .await
                .map_err(|e| {
                    SdkError::Generic(format!(
                        "Signoff failed for {}: {e}",
                        signoff_info.component
                    ))
                })?;

            current_token = sign_response.signed_token.ok_or_else(|| {
                SdkError::Generic(format!(
                    "No signed token returned from {}: {}",
                    signoff_info.component, sign_response.response_msg
                ))
            })?;
        }

        Ok(current_token)
    }

    /// Request a token and automatically collect any required signoffs
    /// This is a convenience method that combines token request and signoff collection
    pub async fn request_token_with_signoffs(
        &self,
        resource: &str,
        operation: &str,
    ) -> Result<String, SdkError> {
        let initial_response = self.request_token(resource, operation).await?;
        self.collect_signoffs(initial_response, resource, operation)
            .await
    }

    /// Verify a token
    ///
    /// This function verifies a token using either the remote Hessra service or
    /// locally using the service's public key if one is configured. This will always
    /// prefer to verify locally if a public key is configured.
    pub async fn verify_token(
        &self,
        token: impl Into<String>,
        subject: impl Into<String>,
        resource: impl Into<String>,
        operation: impl Into<String>,
    ) -> Result<(), SdkError> {
        if self.config.public_key.is_some() {
            self.verify_token_local(
                token.into(),
                subject.into(),
                resource.into(),
                operation.into(),
            )
        } else {
            self.verify_token_remote(
                token.into(),
                subject.into(),
                resource.into(),
                operation.into(),
            )
            .await
            .map(|_| ())
            .map_err(|e| SdkError::Generic(e.to_string()))
        }
    }

    /// Verify a token using the remote Hessra service
    pub async fn verify_token_remote(
        &self,
        token: impl Into<String>,
        subject: impl Into<String>,
        resource: impl Into<String>,
        operation: impl Into<String>,
    ) -> Result<String, SdkError> {
        self.client
            .verify_token(
                token.into(),
                subject.into(),
                resource.into(),
                operation.into(),
            )
            .await
            .map_err(|e| SdkError::Generic(e.to_string()))
    }

    /// Verify a token locally using cached public keys
    pub fn verify_token_local(
        &self,
        token: impl Into<String>,
        subject: impl AsRef<str>,
        resource: impl AsRef<str>,
        operation: impl AsRef<str>,
    ) -> Result<(), SdkError> {
        let public_key_str = match &self.config.public_key {
            Some(key) => key,
            None => return Err(SdkError::Generic("Public key not configured".to_string())),
        };

        let public_key = PublicKey::from_pem(public_key_str.as_str())
            .map_err(|e| SdkError::Token(TokenError::Generic(e.to_string())))?;

        // Convert token to Vec<u8>
        let token_vec = decode_token(&token.into())?;

        verify_biscuit_local(
            token_vec,
            public_key,
            subject.as_ref().to_string(),
            resource.as_ref().to_string(),
            operation.as_ref().to_string(),
        )
        .map_err(SdkError::Token)
    }

    /// Verify a service chain token
    ///
    /// This function verifies a service chain token using either the remote Hessra service or
    /// locally using the service's public key if one is configured. This will always
    /// prefer to verify locally if a public key is configured and a service chain is provided.
    pub async fn verify_service_chain_token(
        &self,
        token: impl Into<String>,
        subject: impl Into<String>,
        resource: impl Into<String>,
        operation: impl Into<String>,
        service_chain: Option<&ServiceChain>,
        component: Option<String>,
    ) -> Result<(), SdkError> {
        match (&self.config.public_key, service_chain) {
            (Some(_), Some(chain)) => self.verify_service_chain_token_local(
                token.into(),
                subject.into(),
                resource.into(),
                operation.into(),
                chain,
                component,
            ),
            _ => self
                .verify_service_chain_token_remote(
                    token.into(),
                    subject.into(),
                    resource.into(),
                    component,
                )
                .await
                .map(|_| ())
                .map_err(|e| SdkError::Generic(e.to_string())),
        }
    }

    /// Verify a service chain token using the remote Hessra service
    pub async fn verify_service_chain_token_remote(
        &self,
        token: impl Into<String>,
        subject: impl Into<String>,
        resource: impl Into<String>,
        component: Option<String>,
    ) -> Result<String, SdkError> {
        self.client
            .verify_service_chain_token(token.into(), subject.into(), resource.into(), component)
            .await
            .map_err(|e| SdkError::Generic(e.to_string()))
    }

    /// Verify a service chain token locally using cached public keys
    pub fn verify_service_chain_token_local(
        &self,
        token: String,
        subject: impl AsRef<str>,
        resource: impl AsRef<str>,
        operation: impl AsRef<str>,
        service_chain: &ServiceChain,
        component: Option<String>,
    ) -> Result<(), SdkError> {
        let public_key_str = match &self.config.public_key {
            Some(key) => key,
            None => return Err(SdkError::Generic("Public key not configured".to_string())),
        };

        let public_key = PublicKey::from_pem(public_key_str.as_str())
            .map_err(|e| SdkError::Token(TokenError::Generic(e.to_string())))?;

        // Convert token to Vec<u8>
        let token_vec = decode_token(&token)?;

        verify_service_chain_biscuit_local(
            token_vec,
            public_key,
            subject.as_ref().to_string(),
            resource.as_ref().to_string(),
            operation.as_ref().to_string(),
            service_chain.to_internal(),
            component,
        )
        .map_err(SdkError::Token)
    }

    /// Attest a service chain token with a new service node attestation
    /// Expects a base64 encoded token string and a service name
    /// Returns a base64 encoded token string
    pub fn attest_service_chain_token(
        &self,
        token: String,
        service: impl Into<String>,
    ) -> Result<String, SdkError> {
        let keypair_str = match &self.config.personal_keypair {
            Some(keypair) => keypair,
            None => {
                return Err(SdkError::Generic(
                    "Personal keypair not configured".to_string(),
                ))
            }
        };

        let public_key_str = match &self.config.public_key {
            Some(key) => key,
            None => return Err(SdkError::Generic("Public key not configured".to_string())),
        };

        // Parse keypair from string to KeyPair
        let keypair = KeyPair::from_private_key_pem(keypair_str.as_str())
            .map_err(|e| SdkError::Token(TokenError::Generic(e.to_string())))?;

        // Parse public key from PEM string
        let public_key = PublicKey::from_pem(public_key_str.as_str())
            .map_err(|e| SdkError::Token(TokenError::Generic(e.to_string())))?;

        // Convert token to Vec<u8>
        let token_vec = decode_token(&token)?;

        // Convert service to String
        let service_str = service.into();

        let token_vec = add_service_node_attestation(token_vec, public_key, &service_str, &keypair)
            .map_err(SdkError::Token)?;

        Ok(encode_token(&token_vec))
    }

    /// Get the public key from the Hessra service
    pub async fn get_public_key(&self) -> Result<String, SdkError> {
        self.client
            .get_public_key()
            .await
            .map_err(|e| SdkError::Generic(e.to_string()))
    }

    /// Get the client used by this SDK instance
    pub fn client(&self) -> &HessraClient {
        &self.client
    }

    /// Get the configuration used by this SDK instance
    pub fn config(&self) -> &HessraConfig {
        &self.config
    }
}

/// Builder for Hessra SDK instances
#[derive(Default)]
pub struct HessraBuilder {
    config_builder: hessra_config::HessraConfigBuilder,
}

impl HessraBuilder {
    /// Create a new Hessra SDK builder
    pub fn new() -> Self {
        Self {
            config_builder: HessraConfig::builder(),
        }
    }

    /// Set the base URL for the Hessra service
    pub fn base_url(mut self, base_url: impl Into<String>) -> Self {
        self.config_builder = self.config_builder.base_url(base_url);
        self
    }

    /// Set the mTLS private key
    pub fn mtls_key(mut self, mtls_key: impl Into<String>) -> Self {
        self.config_builder = self.config_builder.mtls_key(mtls_key);
        self
    }

    /// Set the mTLS client certificate
    pub fn mtls_cert(mut self, mtls_cert: impl Into<String>) -> Self {
        self.config_builder = self.config_builder.mtls_cert(mtls_cert);
        self
    }

    /// Set the server CA certificate
    pub fn server_ca(mut self, server_ca: impl Into<String>) -> Self {
        self.config_builder = self.config_builder.server_ca(server_ca);
        self
    }

    /// Set the port for the Hessra service
    pub fn port(mut self, port: u16) -> Self {
        self.config_builder = self.config_builder.port(port);
        self
    }

    /// Set the protocol to use
    pub fn protocol(mut self, protocol: Protocol) -> Self {
        self.config_builder = self.config_builder.protocol(protocol);
        self
    }

    /// Set the public key for token verification
    pub fn public_key(mut self, public_key: impl Into<String>) -> Self {
        self.config_builder = self.config_builder.public_key(public_key);
        self
    }

    /// Set the personal keypair for service chain attestation
    pub fn personal_keypair(mut self, keypair: impl Into<String>) -> Self {
        self.config_builder = self.config_builder.personal_keypair(keypair);
        self
    }

    /// Build a Hessra SDK instance
    pub fn build(self) -> Result<Hessra, SdkError> {
        let config = self.config_builder.build()?;
        Hessra::new(config)
    }
}

/// Fetch a public key from the Hessra service
///
/// This is a convenience function that doesn't require a fully configured client.
pub async fn fetch_public_key(
    base_url: impl Into<String>,
    port: Option<u16>,
    server_ca: impl Into<String>,
) -> Result<String, SdkError> {
    HessraClient::fetch_public_key(base_url, port, server_ca)
        .await
        .map_err(|e| SdkError::Generic(e.to_string()))
}

/// Fetch a public key from the Hessra service using HTTP/3
///
/// This is a convenience function that doesn't require a fully configured client.
#[cfg(feature = "http3")]
pub async fn fetch_public_key_http3(
    base_url: impl Into<String>,
    port: Option<u16>,
    server_ca: impl Into<String>,
) -> Result<String, SdkError> {
    HessraClient::fetch_public_key_http3(base_url, port, server_ca)
        .await
        .map_err(|e| SdkError::Generic(e.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_service_chain_creation() {
        // Create a simple service chain with two nodes
        let json = r#"[
            {
                "component": "service1",
                "public_key": "ed25519/abcdef1234567890"
            },
            {
                "component": "service2",
                "public_key": "ed25519/0987654321fedcba"
            }
        ]"#;

        let service_chain = ServiceChain::from_json(json).unwrap();
        assert_eq!(service_chain.nodes().len(), 2);
        assert_eq!(service_chain.nodes()[0].component, "service1");
        assert_eq!(
            service_chain.nodes()[0].public_key,
            "ed25519/abcdef1234567890"
        );
        assert_eq!(service_chain.nodes()[1].component, "service2");
        assert_eq!(
            service_chain.nodes()[1].public_key,
            "ed25519/0987654321fedcba"
        );

        // Test adding a node
        let mut chain = ServiceChain::new();
        let node = ServiceNode {
            component: "service3".to_string(),
            public_key: "ed25519/1122334455667788".to_string(),
        };
        chain.add_node(node);
        assert_eq!(chain.nodes().len(), 1);
        assert_eq!(chain.nodes()[0].component, "service3");
    }

    #[test]
    fn test_service_chain_builder() {
        let builder = ServiceChainBuilder::new();
        let node1 = ServiceNode {
            component: "auth".to_string(),
            public_key: "ed25519/auth123".to_string(),
        };
        let node2 = ServiceNode {
            component: "payment".to_string(),
            public_key: "ed25519/payment456".to_string(),
        };

        let chain = builder.add_node(node1).add_node(node2).build();

        assert_eq!(chain.nodes().len(), 2);
        assert_eq!(chain.nodes()[0].component, "auth");
        assert_eq!(chain.nodes()[1].component, "payment");
    }

    #[test]
    fn test_parse_authorization_service_url() {
        // Test URL with https protocol and path
        let (base_url, port) =
            Hessra::parse_authorization_service_url("https://127.0.0.1:4433/sign_token").unwrap();
        assert_eq!(base_url, "127.0.0.1");
        assert_eq!(port, Some(4433));

        // Test URL with http protocol
        let (base_url, port) =
            Hessra::parse_authorization_service_url("http://example.com:8080/api/sign").unwrap();
        assert_eq!(base_url, "example.com");
        assert_eq!(port, Some(8080));

        // Test URL without protocol but with port and path
        let (base_url, port) =
            Hessra::parse_authorization_service_url("test.hessra.net:443/sign_token").unwrap();
        assert_eq!(base_url, "test.hessra.net");
        assert_eq!(port, Some(443));

        // Test URL without protocol and without port
        let (base_url, port) =
            Hessra::parse_authorization_service_url("example.com/api/endpoint").unwrap();
        assert_eq!(base_url, "example.com");
        assert_eq!(port, None);

        // Test URL with just hostname and port (no path)
        let (base_url, port) =
            Hessra::parse_authorization_service_url("https://localhost:8443").unwrap();
        assert_eq!(base_url, "localhost");
        assert_eq!(port, Some(8443));

        // Test hostname only (no protocol, port, or path)
        let (base_url, port) = Hessra::parse_authorization_service_url("api.example.org").unwrap();
        assert_eq!(base_url, "api.example.org");
        assert_eq!(port, None);
    }
}
