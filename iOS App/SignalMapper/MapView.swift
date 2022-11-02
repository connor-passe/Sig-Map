//
//  MapView.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/11/22.
//

import Foundation
import MapKit
import SwiftUI



struct MapView: UIViewRepresentable {
    let powerLoss: PowerLoss
    
    // Required by UIViewRepresentable
    func makeUIView(context: Context) -> MKMapView {
        let region = MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 52.5, longitude: 0), span: MKCoordinateSpan(latitudeDelta: 9, longitudeDelta: 9))
        mapView.region = region
        mapView.delegate = context.coordinator
        return mapView
    }
    
    // Acts as the MapView delegate
    class Coordinator: NSObject, MKMapViewDelegate {
        var parent: MapView
        var powerLoss : PowerLoss
        init(_ parent: MapView, powerLoss: PowerLoss) {
            self.parent = parent
            self.powerLoss = powerLoss
        }
        
        // Places Heatmap
        func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
            let testImage = (powerLoss.array.count == 0) ? UIImage(imageLiteralResourceName: "BetterBase") : processPixels(in: UIImage(imageLiteralResourceName: "BetterBase"), powerLoss: powerLoss)
            if overlay is TileOverlay {
                let temp = TileOverlayView(overlay: overlay, overlayImage: testImage ?? UIImage(imageLiteralResourceName: "test"))
                temp.alpha = 0.5
                return temp
            }
            return MKOverlayRenderer()
        }
        
        // Places Transmitter Pin
        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            let annotationView = TransmitterAnnotationView(annotation: annotation, reuseIdentifier: "Attraction")
            annotationView.canShowCallout = true
            return annotationView
        }
        
        // Generates Heatmap from PowerLoss Array
        func processPixels(in image: UIImage, powerLoss: PowerLoss) -> UIImage? {
            let start = CFAbsoluteTimeGetCurrent()
            guard let inputCGImage = image.cgImage else {
                print("unable to get cgImage")
                return nil
            }
            
            let colorSpace       = CGColorSpaceCreateDeviceRGB()
            let width            = inputCGImage.width
            let height           = inputCGImage.height
            let bytesPerPixel    = 4
            let bitsPerComponent = 8
            let bytesPerRow      = bytesPerPixel * width
            let bitmapInfo       = RGBA32.bitmapInfo
            
            guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: bitsPerComponent, bytesPerRow: bytesPerRow, space: colorSpace, bitmapInfo: bitmapInfo) else {
                print("unable to create context")
                return nil
            }
            context.draw(inputCGImage, in: CGRect(x: 0, y: 0, width: width, height: height))
            
            guard let buffer = context.data else {
                print("unable to get context data")
                return nil
            }
            
            let pixelBuffer = buffer.bindMemory(to: RGBA32.self, capacity: width * height)
            
            for row in 0 ..< Int(height) {
                for column in 0 ..< Int(width) {
                    let offset = row * width + column
                    // For values where there is no PLoss value, set to "Blank"
                    if offset >= powerLoss.array.count {
                        pixelBuffer[offset] = .blank
                    } else {
                        let val = powerLoss.array[offset] ?? 200
                        let num = UInt8(val)
                        // If PLoss is 200 or more, set to Black (Aka outside of calculation range)
                        if val == 200 {
                            pixelBuffer[offset] = .black
                            // Else, set color value to gradient value below
                        } else {
                            pixelBuffer[offset] = RGBA32(red: max(0, (num - 50)*2), green: min(255, 255 - (num - 50)*2),   blue: 0,   alpha: 255)
                        }
                    }
                }
            }
            
            let outputCGImage = context.makeImage()!
            let outputImage = UIImage(cgImage: outputCGImage, scale: image.scale, orientation: image.imageOrientation)
            
            let diff = CFAbsoluteTimeGetCurrent() - start
            print("ProcessPixels Took \(diff) seconds")
            
            return outputImage
        }
        
        // Heatmap color struct
        struct RGBA32: Equatable {
            private var color: UInt32
            
            init(red: UInt8, green: UInt8, blue: UInt8, alpha: UInt8) {
                let red   = UInt32(red)
                let green = UInt32(green)
                let blue  = UInt32(blue)
                let alpha = UInt32(alpha)
                color = (red << 24) | (green << 16) | (blue << 8) | (alpha << 0)
            }
            
            static let black   = RGBA32(red: 0,   green: 0,   blue: 0,   alpha: 255)
            static let blank   = RGBA32(red: 0,   green: 150, blue: 255, alpha: 255)
            
            static let bitmapInfo = CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
            
            static func ==(lhs: RGBA32, rhs: RGBA32) -> Bool {
                return lhs.color == rhs.color
            }
        }
    }
    
    // Required
    func updateUIView(_ uiView: MKMapView, context: Context) {
    }
    
    // Required
    func makeCoordinator() -> Coordinator {
        Coordinator(self, powerLoss: powerLoss)
    }
}
