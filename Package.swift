// swift-tools-version: 5.10
import PackageDescription

let package = Package(
    name: "AnsiSaver",
    products: [
        .library(name: "AnsiSaverCore", targets: ["AnsiSaverCore"]),
        .executable(name: "ansi-saver-cli", targets: ["AnsiSaverCLI"])
    ],
    targets: [
        .target(
            name: "AnsiSaverCore",
            path: "Sources/AnsiSaver",
            exclude: [
                "Animator.swift",
                "AnsiSaverView.swift",
                "ConfigSheet.swift",
                "Configuration.swift",
                "Renderer.swift"
            ],
            sources: [
                "Cache.swift",
                "PackFetcher.swift",
                "ArtSource.swift"
            ]
        ),
        .executableTarget(
            name: "AnsiSaverCLI",
            dependencies: ["AnsiSaverCore"],
            path: "Sources/AnsiSaverCLI"
        ),
        .testTarget(
            name: "AnsiSaverCoreTests",
            dependencies: ["AnsiSaverCore"],
            path: "Tests/AnsiSaverCoreTests"
        )
    ]
)
