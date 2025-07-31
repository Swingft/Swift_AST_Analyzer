//
//  TypealiasVisitor.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/30/25.
//

import SwiftSyntax

final class TypealiasVisitor: SyntaxVisitor {
    var result: [TypealiasInfo] = []
    
    init() {
        super.init(viewMode: .sourceAccurate)
    }
    
    override func visit(_ node: TypeAliasDeclSyntax) -> SyntaxVisitorContinueKind {
        let aliasName = node.name.text
        var protocols: [String] = []
        
        let valueClause = node.initializer
        let type = valueClause.value
        if let composition = type.as(CompositionTypeSyntax.self) {
            let elements = composition.elements
            protocols = elements.map {
                $0.description.trimmingCharacters(in: .whitespacesAndNewlines)
            }
        }
        
        result.append(TypealiasInfo(aliasName: aliasName, protocols: protocols))
        return .skipChildren
    }
}
