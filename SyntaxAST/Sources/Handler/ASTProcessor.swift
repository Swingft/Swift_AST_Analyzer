//
//  Extractor.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

//  SwiftSyntax 소스코드 파싱 및 추출

import Foundation
import SwiftSyntax
import SwiftParser

class Extractor {
    private let sourcePath: String
    private let sourceText: String
    private let syntaxTree: SourceFileSyntax
    var store: ResultStore
    let location: LocationHandler
    
    init(sourcePath: String) throws {
        self.sourcePath = sourcePath
        
        let url = URL(fileURLWithPath: sourcePath)
        self.sourceText = try String(contentsOf: url)
        self.syntaxTree = try Parser.parse(source: sourceText)
        
        self.store = ResultStore()
        self.location = LocationHandler(file: sourcePath, source: sourceText)
    }
    
    func performExtraction() {
        let visitor = Visitor(store: store, location: location)
        visitor.walk(syntaxTree)
    }
}
