//
//  ResultStore.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

//  AST 분석 결과 저장소

class ResultStore {
    private var _results: [IdentifierInfo] = []
    
    func append(_ item: IdentifierInfo) {
        _results.append(item)
    }
    
    func all() -> [IdentifierInfo] {
        return _results
    }
}
