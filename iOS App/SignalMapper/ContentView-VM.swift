//
//  ContentView-ViewModel.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/13/22.
//

import CoreML
import MapKit
import SwiftUI
import TabularData


extension ContentView {
    @MainActor class ViewModel: ObservableObject {
        
        @Published var powerLoss = PowerLoss()
        
        @Published var tile = Tile(id: 0)
        
        // Tile Data
        @Published var tileID = 0
        @Published var tileDF = DataFrame()
        @Published var calculationsDF = DataFrame()
        
        // Transmitter Info
        @Published var transmitterHeight = 141
        @Published var transmitterFrequency: Double = 0
        @Published var transmitterLocation = CLLocation(latitude: 89, longitude: 89)
        
        // UI State Variables
        @Published var showingMapOverlay = false
        @Published var showingTransmitterPin = false
        @Published var showingFrequencySelection = false
        @Published var showingProgressView = false
        @Published var showingDownloadOptions = false
        @Published var showingFrequencyAlert = false
        @Published var showingHeatmapPreferences = false
        
        // DataFrame print preferences
        let formattingOptions = FormattingOptions(maximumLineWidth: 250, maximumCellWidth: 10, maximumRowCount: 5, includesColumnTypes: true)
        
        // Logical Conditions
        @Published var changeToGenerate = false
        @Published var enableMultiThreading = false
        @Published var checkFrequencyValidity = false
        @Published var calculationRadius: Double = 5
        var ableToCreateHeatmap: Bool {
            transmitterLocation.coordinate.latitude != 89
        }
        
        

        // Top-Level Functions
        
        // Loads tile data
        func loadMap(id: Int) {
            powerLoss.array = [Double?]()
            tile = Tile(id: id)
            tileID = id
            readCSV()
            removeTransmitterAnnotations()
            updateTransmitterLocation(coordinate: CLLocationCoordinate2D(latitude: 89, longitude: 89))
            showingMapOverlay = true
            updateMapOverlayViews()
        }
        
        // Places transmitter pin on map
        func placeTransmitter() {
            removeTransmitterAnnotations()
            updateTransmitterLocation(coordinate: mapView.centerCoordinate)
            changeToGenerate = true
        }
        
        // Validates frequency value, shows alert if not valid
        func attemptFrequencySave() {
            if (transmitterFrequency > 0) {
                showingFrequencySelection = false
                changeToGenerate = true
            } else {
                showingFrequencyAlert = true
            }
        }
        
        // Creates heatmap
        func generateHeatmap() {
            showingProgressView = true
            changeToGenerate = false
            if enableMultiThreading {
                DispatchQueue.background(background: {
                    // do something in background
                    self.prepareData()
                    self.MLCalculation()
                }, completion:{
                    // when background job finished, do something in main thread
                    self.updateMapOverlayViews()
                    self.showingProgressView = false
                })
            } else {
                prepareData()
                MLCalculation()
                updateMapOverlayViews()
                showingProgressView = false
            }
        }
        
        // Helper Functions
        
        // Removes and adds new overlay
        func updateMapOverlayViews() {
            mapView.removeOverlays(mapView.overlays)
            if showingMapOverlay {
                let overlay = TileOverlay(tile: tile)
                mapView.addOverlay(overlay)
            }
        }
        
        // Removes TransmitterAnnotations
        func removeTransmitterAnnotations() {
            mapView.removeAnnotations(mapView.annotations)
        }
        
        // Updates Transmitter Location
        func updateTransmitterLocation(coordinate: CLLocationCoordinate2D) {
            transmitterLocation = CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude)
            if transmitterLocation.coordinate.longitude != 89 {
                showingTransmitterPin = true
            }
            let annotation = TransmitterAnnotation(coordinate: CLLocationCoordinate2D(latitude: transmitterLocation.coordinate.latitude, longitude: transmitterLocation.coordinate.longitude))
            mapView.addAnnotation(annotation)
        }
        
        // Loads CSV of Tile data:  lattitude, longitude, elevation
        func readCSV() {
            let start = CFAbsoluteTimeGetCurrent()
            let options = CSVReadingOptions(hasHeaderRow: true, delimiter: ",")
            guard let fileUrl = Bundle.main.url(forResource: "stevenage\(tileID)", withExtension: "csv") else {
                fatalError("Error creating Url")
            }
            tileDF = DataFrame()
            tileDF = try! DataFrame(contentsOfCSVFile: fileUrl, options: options)
            let diff = CFAbsoluteTimeGetCurrent() - start
            print("ReadCSV Took \(diff) seconds")
        }
        
        // Prepares / Wrangles Data for ML Model
        func prepareData() {
            let start = CFAbsoluteTimeGetCurrent()
            calculationsDF = tileDF
            calculationsDF.combineColumns("Latitude", "Longitude", into: "Distance") { (latitude: Double?, longitude: Double?) -> Double? in
                guard let latitude = latitude, let longitude = longitude else {
                    return nil
                }
                let recieverLocation = CLLocation(latitude: latitude, longitude: longitude)
                return recieverLocation.distance(from: CLLocation(latitude: transmitterLocation.coordinate.latitude, longitude: transmitterLocation.coordinate.longitude)) / 1000.0
            }
            
            calculationsDF.transformColumn("Elevation") { (elevation: Int) in
                Double(elevation - transmitterHeight)
            }
            
            let diff = CFAbsoluteTimeGetCurrent() - start
            print("CalcData Took \(diff) seconds")
        }
        
        // Perform Power Loss ML Calculation
        func MLCalculation() {
            let start = CFAbsoluteTimeGetCurrent()
            let config = MLModelConfiguration()
            let model = try! PLossModel(configuration: config)
        
            calculationsDF.combineColumns("Elevation", "Distance", into: "PLoss") { (elevation: Double?, distance: Double?) -> Double? in
                    if (distance! > calculationRadius) {
                        return 200
                    } else {
                        let prediction = try! model.prediction(Frequency: transmitterFrequency, Distance: distance!, Height_Difference: elevation! - 142)
                        return prediction.Power_Loss
                    }
            }
            powerLoss.array =  calculationsDF["PLoss", Double.self]
            let diff = CFAbsoluteTimeGetCurrent() - start
            print("MLTransform Took \(diff) seconds")
        }
    }
}
    
        
