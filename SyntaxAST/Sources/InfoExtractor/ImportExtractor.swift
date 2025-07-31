//
//  ImportExtractor.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/25/25.
//

import SwiftSyntax
import Foundation

class ImportExtractor: SyntaxVisitor {
    var imports: Set<String> = []
    
    init() {
        super.init(viewMode: .sourceAccurate)
    }
    
    override func visit(_ node: ImportDeclSyntax) -> SyntaxVisitorContinueKind {
        if let path = node.path.first?.name.text {
            imports.insert(path)
        }
        return .skipChildren
    }
    
    func writeImports() -> Bool {
        let outputFile = URL(fileURLWithPath: "../output/").appendingPathComponent("import_list.txt")
        let content = imports.joined(separator: "\n") + "\n"
        if content.contains("UIKit") || content.contains("SwiftUI") {
            return true
        }

        do {
            if !FileManager.default.fileExists(atPath: outputFile.path) {
                FileManager.default.createFile(atPath: outputFile.path, contents: nil)
            }
            
            let fileHandle = try FileHandle(forWritingTo: outputFile)
            fileHandle.seekToEndOfFile()
            if let data = content.data(using: .utf8) {
                fileHandle.write(data)
            }
            
        } catch {
            print("Failed to write: \(error)")
        }
        return false
    }
}
