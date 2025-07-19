//
//  Visitor.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

//  AST 탐색

import SwiftSyntax

class Visitor: SyntaxVisitor {
    private let store: ResultStore
    private let location: LocationHandler
    
    init(store:  ResultStore, location: LocationHandler) {
        self.store = store
        self.location = location
        super.init(viewMode: .sourceAccurate)
    }
    
    override func visit(_ node: ProtocolDeclSyntax) -> SyntaxVisitorContinueKind {
        let info = ProtocolInfoExtractor.extract(from: node, locationHandler: location)
        store.append(info)
        return .skipChildren
    }
    
    override func visit(_ node: ClassDeclSyntax) -> SyntaxVisitorContinueKind {
        let info = ClassInfoExtractor.extract(from: node, locationHandler: location)
        store.append(info)
        return .skipChildren
    }
    
    override func visit(_ node: StructDeclSyntax) -> SyntaxVisitorContinueKind {
        let info = StructInfoExtractor.extract(from: node, locationHandler: location)
        store.append(info)
        return .skipChildren
    }
    
    override func visit(_ node: ExtensionDeclSyntax) -> SyntaxVisitorContinueKind {
        let info = ExtensionInfoExtractor.extractor(from: node, locationHandler: location)
        store.append(info)
        return .skipChildren
    }
    
    override func visit(_ node: FunctionDeclSyntax) -> SyntaxVisitorContinueKind {
        let info = FunctionInfoExtractor.extract(from: node, locationHandler: location)
        store.append(info)
        return .skipChildren
    }
    
    override func visit(_ node: VariableDeclSyntax) -> SyntaxVisitorContinueKind {
        let infos = VariableInfoExtractor.extract(from: node, locationHandler: location)
        
        for info in infos {
            store.append(info)
        }
        
        return .skipChildren
    }
}
