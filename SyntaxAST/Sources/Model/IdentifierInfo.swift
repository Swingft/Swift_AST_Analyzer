//
//  IdentifierInfo.swift
//  SyntaxAST
//
//  Created by 백승혜 on 7/15/25.
//

struct IdentifierInfo: Codable {
    var A_name: String                        //선언 이름
    var B_kind: String                        
    var C_accessLevel: String                 //접근제어자
    var D_attributes: [String]                //속성
    var E_adoptedClassProtocols: [String]?    //프로토콜 채택
    var F_location: String                    //위치
    var G_members: [IdentifierInfo]?
    var H_initialValue: String?               //초기값
}
