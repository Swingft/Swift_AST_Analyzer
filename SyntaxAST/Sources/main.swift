// The Swift Programming Language
// https://docs.swift.org/swift-book

import Foundation

let sourcePath = CommandLine.arguments[1]
let outputDir = "../output/source_json"

do {
    let extractor = try Extractor(sourcePath: sourcePath)
    extractor.performExtraction()
    
    let result = extractor.store.all()
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let jsonData = try encoder.encode(result)

    let sourceURL = URL(fileURLWithPath: sourcePath)
    let fileName = sourceURL.deletingPathExtension().lastPathComponent
    let outputURL = URL(fileURLWithPath: outputDir)
            .appendingPathComponent(fileName)
            .appendingPathExtension("json")
    try jsonData.write(to: outputURL)
    
} catch {
    print("Error: \(error)")
    exit(1)
}
