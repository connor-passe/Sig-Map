//
//  String-FileExtensions.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/6/22.
//

import Foundation

extension String {
    func fileName() -> String {
        return URL(fileURLWithPath: self).deletingPathExtension().lastPathComponent
    }
    
    func fileExtension() -> String {
        URL(fileURLWithPath: self).pathExtension
    }
}
