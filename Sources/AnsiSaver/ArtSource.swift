import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif


public protocol ArtSource {
    func loadArtPaths(completion: @escaping ([String]) -> Void)
}

public final class FolderSource: ArtSource {

    private let folderPath: String

    public init(folderPath: String) {
        self.folderPath = folderPath
    }

    public func loadArtPaths(completion: @escaping ([String]) -> Void) {
        let fm = FileManager.default
        guard let contents = try? fm.contentsOfDirectory(atPath: folderPath) else {
            completion([])
            return
        }

        let ansiExtensions: Set<String> = ["ans", "ansi", "asc", "diz", "ice", "bin", "xb", "pcb", "adf"]

        let paths = contents
            .filter { name in
                let ext = (name as NSString).pathExtension.lowercased()
                return ansiExtensions.contains(ext)
            }
            .map { (folderPath as NSString).appendingPathComponent($0) }

        completion(paths)
    }
}

public final class PackSource: ArtSource {

    private let packURL: String

    public init(packURL: String) {
        self.packURL = packURL
    }

    public func loadArtPaths(completion: @escaping ([String]) -> Void) {
        let packName = extractPackName(from: packURL)

        PackFetcher.fetchFileList(packURL: packURL) { filenames in
            guard !filenames.isEmpty else {
                completion([])
                return
            }

            let queue = DispatchQueue(label: "com.lardissone.AnsiSaver.packSource")
            var localPaths: [String] = []
            let group = DispatchGroup()

            for filename in filenames {
                let localPath = Cache.ansPath(forPack: packName, file: filename)

                if Cache.exists(localPath) {
                    queue.sync { localPaths.append(localPath) }
                    continue
                }

                group.enter()
                PackFetcher.downloadFile(packURL: self.packURL, filename: filename, to: localPath) { success in
                    if success {
                        queue.sync { localPaths.append(localPath) }
                    }
                    group.leave()
                }
            }

            group.notify(queue: .main) {
                completion(localPaths)
            }
        }
    }

    private func extractPackName(from url: String) -> String {
        let trimmed = url.hasSuffix("/") ? String(url.dropLast()) : url
        return (trimmed as NSString).lastPathComponent
    }
}

public final class URLSource: ArtSource {

    private let fileURLs: [String]

    public init(fileURLs: [String]) {
        self.fileURLs = fileURLs
    }

    public func loadArtPaths(completion: @escaping ([String]) -> Void) {
        let queue = DispatchQueue(label: "com.lardissone.AnsiSaver.urlSource")
        var localPaths: [String] = []
        let group = DispatchGroup()

        for urlString in fileURLs {
            let localPath = Cache.urlCachePath(for: urlString)

            if Cache.exists(localPath) {
                queue.sync { localPaths.append(localPath) }
                continue
            }

            guard let url = URL(string: urlString) else { continue }

            group.enter()
            let task = URLSession.shared.dataTask(with: url) { data, _, error in
                if let data = data, error == nil {
                    Cache.write(data, to: localPath)
                    queue.sync { localPaths.append(localPath) }
                }
                group.leave()
            }
            task.resume()
        }

        group.notify(queue: .main) {
            completion(localPaths)
        }
    }
}