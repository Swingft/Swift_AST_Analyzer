//
//  LocationHelper.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

//  위치 정보 변환

import SwiftSyntax

class LocationHandler {
    private let converter: SourceLocationConverter
    
    init(file: String, source: String) {
        self.converter = SourceLocationConverter(file: file, source: source)
    }
    
    func findLocation(of node: SyntaxProtocol) -> String {
        let location = node.startLocation(converter: converter)
        return "Line: \(location.line), Column: \(location.column)"
    }
}
