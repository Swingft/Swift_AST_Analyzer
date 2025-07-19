// The Swift Programming Language
// https://docs.swift.org/swift-book

import Foundation

let sourcePath = CommandLine.arguments[1]

do {
    let extractor = try Extractor(sourcePath: sourcePath)
    extractor.performExtraction()
    
    let result = extractor.store.all()
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let jsonData = try encoder.encode(result)
    
    let outputURL = URL(fileURLWithPath: sourcePath)
            .deletingPathExtension()
            .appendingPathExtension("json")
    try jsonData.write(to: outputURL)
        print("Extraction complete! JSON saved to: \(outputURL.path)")
} catch {
    print("Error: \(error)")
    exit(1)
}
