import Foundation
import AnsiSaverCore

private enum CLIError: Error {
    case invalidArguments
}

@main
struct AnsiSaverCLI {
    static func main() {
        do {
            try run()
        } catch {
            fputs("Error: \(error)\n", stderr)
            printUsage()
            exit(1)
        }
    }

    private static func run() throws {
        let args = Array(CommandLine.arguments.dropFirst())
        guard let command = args.first else {
            throw CLIError.invalidArguments
        }

        switch command {
        case "fetch-pack":
            guard args.count == 2 else { throw CLIError.invalidArguments }
            fetchPack(args[1])
        case "scan-folder":
            guard args.count == 2 else { throw CLIError.invalidArguments }
            scanFolder(args[1])
        default:
            throw CLIError.invalidArguments
        }
    }

    private static func fetchPack(_ url: String) {
        let semaphore = DispatchSemaphore(value: 0)
        PackFetcher.fetchFileList(packURL: url) { files in
            files.forEach { print($0) }
            semaphore.signal()
        }
        _ = semaphore.wait(timeout: .now() + 30)
    }

    private static func scanFolder(_ path: String) {
        FolderSource(folderPath: path).loadArtPaths { paths in
            paths.forEach { print($0) }
        }
    }

    private static func printUsage() {
        let usage = """
        ansi-saver-cli (Windows/macOS compatible helper)

        Usage:
          ansi-saver-cli fetch-pack <16colo-pack-url>
          ansi-saver-cli scan-folder <folder-path>
        """
        print(usage)
    }
}
