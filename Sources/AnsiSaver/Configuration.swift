import Foundation
import ScreenSaver

struct Configuration {

    private static let moduleName = "com.lardissone.AnsiSaver"

    private enum Key {
        static let packURLs = "packURLs"
        static let fileURLs = "fileURLs"
        static let localFolderBookmark = "localFolderBookmark"
        static let transitionMode = "transitionMode"
        static let scrollSpeed = "scrollSpeed"
    }

    var packURLs: [String]
    var fileURLs: [String]
    var localFolderBookmark: Data?
    var transitionMode: Int
    var scrollSpeed: Double

    var localFolderPath: String? {
        guard let bookmark = localFolderBookmark else { return nil }
        return Self.resolveBookmark(bookmark)
    }

    static func load() -> Configuration {
        let defaults = screenSaverDefaults()
        return Configuration(
            packURLs: defaults.stringArray(forKey: Key.packURLs) ?? [],
            fileURLs: defaults.stringArray(forKey: Key.fileURLs) ?? [],
            localFolderBookmark: defaults.data(forKey: Key.localFolderBookmark),
            transitionMode: defaults.integer(forKey: Key.transitionMode),
            scrollSpeed: defaults.object(forKey: Key.scrollSpeed) != nil
                ? defaults.double(forKey: Key.scrollSpeed)
                : 50.0
        )
    }

    func save() {
        let defaults = Self.screenSaverDefaults()
        defaults.set(packURLs, forKey: Key.packURLs)
        defaults.set(fileURLs, forKey: Key.fileURLs)
        defaults.set(localFolderBookmark, forKey: Key.localFolderBookmark)
        defaults.set(transitionMode, forKey: Key.transitionMode)
        defaults.set(scrollSpeed, forKey: Key.scrollSpeed)
        defaults.synchronize()
    }

    static func createBookmark(for url: URL) -> Data? {
        return try? url.bookmarkData(
            options: [.withSecurityScope],
            includingResourceValuesForKeys: nil,
            relativeTo: nil
        )
    }

    static func resolveBookmark(_ bookmark: Data) -> String? {
        var isStale = false
        guard let url = try? URL(
            resolvingBookmarkData: bookmark,
            options: [.withSecurityScope],
            relativeTo: nil,
            bookmarkDataIsStale: &isStale
        ) else { return nil }

        if url.startAccessingSecurityScopedResource() {
            return url.path
        }
        return url.path
    }

    private static func screenSaverDefaults() -> UserDefaults {
        return ScreenSaverDefaults(forModuleWithName: moduleName)!
    }
}
