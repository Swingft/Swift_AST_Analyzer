//
//  IdentifierInfo.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

struct IdentifierInfo: Codable {
    var A_name: String
    var B_kind: String                        
    var C_accessLevel: String
    var D_attributes: [String]
    var E_adoptedClassProtocols: [String]?
    var F_location: String
    var G_members: [IdentifierInfo]?
    var H_initialValue: String?
    var I_parameters: [String]?
    var J_returnType: String?
}
