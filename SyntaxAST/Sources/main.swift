// The Swift Programming Language
// https://docs.swift.org/swift-book

import Foundation

let sourceListPath = CommandLine.arguments[1]
let externalSourceListPath = CommandLine.arguments[2]

let internalH = InternalHandler(sourceListPath: sourceListPath)
try internalH.readAndProcess()

let externalH = ExternalHandler(sourceListPath: externalSourceListPath)
try externalH.readAndProcess()
