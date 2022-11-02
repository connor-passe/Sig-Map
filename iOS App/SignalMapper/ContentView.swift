//
//  ContentView.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/3/22.
//

import CoreML
import MapKit
import SwiftUI
import TabularData


let mapView = MKMapView(frame: UIScreen.main.bounds)

struct ContentView: View {
    @StateObject private var viewModel = ViewModel()
    
    var body: some View {
        ZStack {
            // Base Map
            MapView(powerLoss: viewModel.powerLoss)
                .ignoresSafeArea()

            VStack {
                // Menu Button Dock
                HStack{
                    // Download Tile Button
                    Button() {
                        viewModel.showingDownloadOptions = true
                    } label: {
                        Image(systemName: "square.and.arrow.down")
                            .modifier(ButtonMod())
                    }
                    .confirmationDialog("Select Map Region", isPresented: $viewModel.showingDownloadOptions) {
                        Button("North-West United Kingdom") {
                            viewModel.loadMap(id: 0)
                        }
                        Button("North-East United Kingdom") {
                            viewModel.loadMap(id: 1)
                        }
                        Button("South-West United Kingdom") {
                            viewModel.loadMap(id: 2)
                        }
                        Button("South-East United Kingdom") {
                            viewModel.loadMap(id: 3)
                        }
                    }
                    
                    // Place Transmitter Pin Button
                    Button {
                        viewModel.placeTransmitter()
                        
                    } label: {
                        Image(systemName: "mappin")
                            .modifier(ButtonMod())
                            .opacity(viewModel.showingMapOverlay ? 1 : 0.5)
                    }
                    .disabled(viewModel.showingMapOverlay == false)
                    
                    // Generate Heatmap Button
                    Button {
                        viewModel.showingHeatmapPreferences = true
                    } label: {
                        Image(systemName: "map")
                            .modifier(ButtonMod())
                            .opacity(viewModel.ableToCreateHeatmap ? 1 : 0.5)
                    }
                    .disabled(viewModel.ableToCreateHeatmap == false)
                    .sheet(isPresented: $viewModel.showingHeatmapPreferences) {
                        // Heatmap Preferences Form
                        NavigationView {
                            Form {
                                Section {
                                    TextField("GHz", value: $viewModel.transmitterFrequency, format: .number)
                                        .keyboardType(.decimalPad)
                                } header: {
                                    Text("Transmission Frequency in GHz")
                                }
                                
                                Section {
                                    Stepper("\(viewModel.calculationRadius.formatted()) Km", value: $viewModel.calculationRadius, in: 1...10, step: 1)
                                } header: {
                                    Text("Transmission Radius in Km")
                                }
                            }
                            .navigationTitle("Heatmap Preferences")
                            .toolbar {
                                Button("Generate")  {
                                    viewModel.attemptFrequencySave()
                                    if viewModel.showingFrequencyAlert == false {
                                        viewModel.showingHeatmapPreferences = false
                                        viewModel.generateHeatmap()
                                    }
                                }
                            }
                            .alert("Invalid Frequency", isPresented: $viewModel.showingFrequencyAlert) {
                                Button("Ok", role: .cancel) { }
                            } message: {
                                Text("Enter a positive frequency value")
                            }
                        }
                    }
                }
                Spacer()
            }
            // Center Target
            Color(.black)
                .opacity(viewModel.showingProgressView ? 0.5 : 0)
                .ignoresSafeArea()
            Image(systemName: "scope")
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
