//
//  TransmitterAnnotation.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/13/22.
//

import MapKit

class TransmitterAnnotation: NSObject, MKAnnotation {
    let coordinate: CLLocationCoordinate2D
    let title: String? = "Test"
    
init (coordinate: CLLocationCoordinate2D) {
    self.coordinate = coordinate
    }
}
