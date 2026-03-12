import XCTest
@testable import AnsiSaverCore

final class AnsiSaverCoreTests: XCTestCase {
    func testParseANSFilenamesIncludesAnsiFormats() {
        let html = """
        <a href=\"/pack/a/raw/file.ans\">file.ans</a>
        <a href=\"/pack/a/raw/demo.ICE\">demo.ICE</a>
        """
        let files = PackFetcher.parseANSFilenames(from: html)
        XCTAssertEqual(files.count, 2)
    }

    func testCachePathIsDeterministic() {
        let one = Cache.urlCachePath(for: "https://example.com/demo.ans")
        let two = Cache.urlCachePath(for: "https://example.com/demo.ans")
        XCTAssertEqual(one, two)
    }
}
