//
//  SignalMapOverlay.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/5/22.
//

import MapKit

class TileOverlay: NSObject, MKOverlay {
  let coordinate: CLLocationCoordinate2D
  let boundingMapRect: MKMapRect
  
  init(tile: Tile) {
    boundingMapRect = tile.overlayBoundingMapRect
    coordinate = tile.midCoordinate
  }
}
