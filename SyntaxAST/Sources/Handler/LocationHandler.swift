//
//  LocationHelper.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

//  위치 정보 변환

import SwiftSyntax
import Foundation

class LocationHandler {
    private let converter: SourceLocationConverter
    private let fileName: String
    
    init(file: String, source: String) {
        self.converter = SourceLocationConverter(file: file, source: source)
        self.fileName = (file as NSString).lastPathComponent
    }
    
    func findLocation(of node: SyntaxProtocol) -> String {
        let location = node.startLocation(converter: converter)
        return "\(fileName) - Line: \(location.line), Column: \(location.column)"
    }
}
