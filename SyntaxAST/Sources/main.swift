// The Swift Programming Language
// https://docs.swift.org/swift-book

import Foundation

let sourceListPath = CommandLine.arguments[1]
let outputDir = "../output/source_json"
let ui_outputDir = "../output/ui_source_json"
let typealias_outputDir = "../output/typealias_json"

do {
    let fileList = try String(contentsOfFile: sourceListPath)
    let sourcePaths = fileList.split(separator: "\n").map { String($0) }
    
    var typeResult: [TypealiasInfo] = []
    
    for sourcePath in sourcePaths {
        do {
            let extractor = try Extractor(sourcePath: sourcePath)
            let (isUIKit, typealiasResult) = extractor.performExtraction()
            typeResult.append(contentsOf: typealiasResult)
            
            let result = extractor.store.all()
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            let jsonData = try encoder.encode(result)

            let sourceURL = URL(fileURLWithPath: sourcePath)
            let fileName = sourceURL.path
                .replacingOccurrences(of: "/", with: "_")
                .replacingOccurrences(of: ".", with: "_")
            var outputURL = URL(fileURLWithPath: outputDir)
                    .appendingPathComponent(fileName)
                    .appendingPathExtension("json")
            if isUIKit {
                outputURL = URL(fileURLWithPath: ui_outputDir)
                        .appendingPathComponent(fileName)
                        .appendingPathExtension("json")
            }
            try jsonData.write(to: outputURL)
        } catch {
            print("Error: \(error)")
        }
    }
    
    if !typeResult.isEmpty {
        let fileName = "typealias"
        var outputURL = URL(fileURLWithPath: typealias_outputDir)
            .appendingPathComponent(fileName)
            .appendingPathExtension("json")
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let jsonData = try encoder.encode(typeResult)
        try jsonData.write(to: outputURL)
    }
    
} catch {
    print("Error: \(error)")
    exit(1)
}

