//
//  ButtonMod.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/25/22.
//

import SwiftUI

// ViewModifier for main buttons
struct ButtonMod: ViewModifier {
    func body(content: Content) -> some View {
            content
            .padding()
            .background(.black.opacity(0.75))
            .foregroundColor(.white)
            .font(.title)
            .clipShape(Circle())
        }
}
