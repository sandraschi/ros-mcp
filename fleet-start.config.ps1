# Per-repo fleet start config for ros-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'ros-mcp'
    BackendPort  = 11050
    FrontendPort = 11051
    HealthPath   = '/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'web_sota.backend.server:app'
        WorkDir       = '.'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '11050' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
