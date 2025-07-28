//
//  EnumInfoExtractor.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/25/25.
//

import SwiftSyntax

struct EnumInfoExtractor {
    static func extract(from node: EnumDeclSyntax, locationHandler locationHandler: LocationHandler) -> IdentifierInfo {
        let name = node.name.text
        let kind = "enum"
        
        let accessLevels = ["private", "fileprivate", "internal", "public", "open"]
        let accessLevel = node.modifiers.compactMap {
            modifier -> String? in
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
        
        let adoptedClassProtocols: [String]
        if let inheritanceClause = node.inheritanceClause {
            adoptedClassProtocols = inheritanceClause.inheritedTypeCollection.compactMap {
                $0.typeName.description.trimmingCharacters(in: .whitespacesAndNewlines)
            }
        } else {
            adoptedClassProtocols = []
        }
        
        let location = locationHandler.findLocation(of: node)
        
        var memberList: [IdentifierInfo] = []
        for member in node.memberBlock.members {
            let decl = member.decl
            
            if let caseDecl = decl.as(EnumCaseDeclSyntax.self) {
                let accessLevels = ["private", "fileprivate", "internal", "public", "open"]
                let accessLevel = caseDecl.modifiers.compactMap {
                    modifier -> String? in
                    let name = modifier.name.text
                    return accessLevels.contains(name) ? name : nil
                }.first ?? "internal"
                
                let modifiers = caseDecl.modifiers ?? []
                let otherMods = modifiers.compactMap { modifier -> String? in
                    let name = modifier.name.text
                    return accessLevels.contains(name) ? nil : name
                }
                var attributes = (caseDecl.attributes ?? []).compactMap {
                    $0.as(AttributeSyntax.self)?.attributeName.description.trimmingCharacters(in: .whitespacesAndNewlines)
                }
                attributes.append(contentsOf: otherMods)
                
                for element in caseDecl.elements {
                    let name = element.identifier.text
                    let info = IdentifierInfo(
                        A_name: name,
                        B_kind: "case",
                        C_accessLevel: accessLevel,
                        D_attributes: attributes,
                        F_location: locationHandler.findLocation(of: element)
                    )
                    memberList.append(info)
                }
            }
            else if let varDecl = decl.as(VariableDeclSyntax.self) {
                let info = VariableInfoExtractor.extract(from: varDecl, locationHandler: locationHandler)
                memberList.append(contentsOf: info)
            }
            else if let funcDecl = decl.as(FunctionDeclSyntax.self) {
                let info = FunctionInfoExtractor.extract(from: funcDecl, locationHandler: locationHandler)
                memberList.append(info)
            }
            else if let enumDecl = decl.as(EnumDeclSyntax.self) {
                let info = EnumInfoExtractor.extract(from: enumDecl, locationHandler: locationHandler)
                memberList.append(info)
            }
        }
        
        return IdentifierInfo(
            A_name: name,
            B_kind: kind,
            C_accessLevel: accessLevel,
            D_attributes: attributes,
            E_adoptedClassProtocols: adoptedClassProtocols,
            F_location: location,
            G_members: memberList
        )
    }
}
