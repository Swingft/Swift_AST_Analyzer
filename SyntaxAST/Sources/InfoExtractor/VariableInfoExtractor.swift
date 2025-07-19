//
//  VariableInfoExtractor.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

import SwiftSyntax

struct VariableInfoExtractor {
    static func extract(from node: VariableDeclSyntax, locationHandler locationHandler: LocationHandler) -> [IdentifierInfo] {
        var variableList: [IdentifierInfo] = []
        
        let kind = "variable"
        
        let accessLevels = ["private", "fileprivate", "internal", "public", "open"]
        let accessLevel = node.modifiers.compactMap { modifier -> String? in
            let name = modifier.name.text
            return accessLevels.contains(name) ? name : nil
        }.first ?? "internal"
        
        let modifiers = node.modifiers ?? []
        let otherMods = modifiers.compactMap { modifier -> String? in
            let name = modifier.name.text
            return accessLevels.contains(name) ? nil : name
        }
        var attributes = (node.attributes ?? []).compactMap {
            $0.as(AttributeSyntax.self)?.attributeName.description.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        attributes.append(contentsOf: otherMods)
        
        for binding in node.bindings {
            if let pattern = binding.pattern.as(IdentifierPatternSyntax.self) {
                let name = pattern.identifier.text
                let location = locationHandler.findLocation(of: node)
                
                let initialValue = binding.initializer?.value.description.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
                
                let info = IdentifierInfo(
                    A_name: name,
                    B_kind: kind,
                    C_accessLevel: accessLevel,
                    D_attributes: attributes,
                    F_location: location,
                    H_initialValue: initialValue
                )
                variableList.append(info)
            }
        }
        
        return variableList
    }
}
