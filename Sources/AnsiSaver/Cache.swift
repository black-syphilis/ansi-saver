import Foundation
#if canImport(CommonCrypto)
import CommonCrypto
#endif

public enum Cache {

    private static let basePath: String = {
        let fm = FileManager.default
        if let cacheURL = fm.urls(for: .cachesDirectory, in: .userDomainMask).first {
            return cacheURL.appendingPathComponent("AnsiSaver", isDirectory: true).path
        }
        return URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent("AnsiSaver", isDirectory: true).path
    }()

    public static func ansPath(forPack pack: String, file: String) -> String {
        return (basePath as NSString)
            .appendingPathComponent("packs/\(pack)/\(file)")
    }

    public static func pngPath(forAnsPath ansPath: String) -> String {
        return (ansPath as NSString).deletingPathExtension + ".png"
    }

    public static func urlCachePath(for urlString: String) -> String {
        let hash = stableHash(urlString)
        return (basePath as NSString)
            .appendingPathComponent("urls/\(hash).ans")
    }

    public static func read(_ path: String) -> Data? {
        return FileManager.default.contents(atPath: path)
    }

    public static func write(_ data: Data, to path: String) {
        let dir = (path as NSString).deletingLastPathComponent
        try? FileManager.default.createDirectory(
            atPath: dir, withIntermediateDirectories: true)
        FileManager.default.createFile(atPath: path, contents: data)
    }

    public static func exists(_ path: String) -> Bool {
        return FileManager.default.fileExists(atPath: path)
    }

    public static func clearPacks() {
        let packsDir = (basePath as NSString).appendingPathComponent("packs")
        try? FileManager.default.removeItem(atPath: packsDir)
    }

    public static func clearAll() {
        try? FileManager.default.removeItem(atPath: basePath)
    }

    private static func stableHash(_ string: String) -> String {
        #if canImport(CommonCrypto)
        let data = Data(string.utf8)
        var hash = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
        data.withUnsafeBytes { buffer in
            _ = CC_SHA256(buffer.baseAddress, CC_LONG(data.count), &hash)
        }
        return hash.map { String(format: "%02x", $0) }.joined()
        #else
        // Fallback for non-Apple targets where CommonCrypto isn't available.
        // FNV-1a (64-bit) is stable and sufficient for cache key derivation.
        var value: UInt64 = 0xcbf29ce484222325
        for byte in string.utf8 {
            value ^= UInt64(byte)
            value &*= 0x100000001b3
        }
        return String(format: "%016llx", value)
        #endif
    }
}
