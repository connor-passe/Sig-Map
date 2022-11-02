//
//  Signal.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/5/22.
//

import MapKit

class Tile {
    // 0 Index mapping of tiles
    var tileID: Int
    
    // Dictionaries of coordinates
    let latCoordinates: [[Double]] = [[53, 52, 52.5], [53, 52, 52.5], [52, 51, 51.5], [52, 51, 51.5]]
    let longCoordinates: [[Double]] = [[0, -1, -0.5], [1, 0, 0.5], [0, -1, -0.5], [1, 0, 0.5]]

    // Required Coordinates
    var overlayTopRightCoordinate = CLLocationCoordinate2D()
    var overlayBottomLeftCoordinate = CLLocationCoordinate2D()
    var midCoordinate = CLLocationCoordinate2D()
    
    // Calculated Coordinates
    var overlayTopLeftCoordinate: CLLocationCoordinate2D {
        return CLLocationCoordinate2D(latitude: overlayTopRightCoordinate.latitude, longitude: overlayBottomLeftCoordinate.longitude)
    }
    var overlayBottomRightCoordinate: CLLocationCoordinate2D {
        return CLLocationCoordinate2D(latitude: overlayBottomLeftCoordinate.latitude, longitude: overlayTopRightCoordinate.longitude)
    }
    
    // MKMap Rectangle
    var overlayBoundingMapRect: MKMapRect {
        let topLeft = MKMapPoint(overlayTopLeftCoordinate)
        let topRight = MKMapPoint(overlayTopRightCoordinate)
        let bottomLeft = MKMapPoint(overlayBottomLeftCoordinate)

        return MKMapRect(x: topLeft.x, y: topLeft.y, width: fabs(topLeft.x - topRight.x), height: fabs(topLeft.y - bottomLeft.y))
    }
    
    // Initializer
    init(id: Int) {
        tileID = id
        overlayTopRightCoordinate = CLLocationCoordinate2D(latitude: latCoordinates[id][0], longitude: longCoordinates[id][0])
        overlayBottomLeftCoordinate = CLLocationCoordinate2D(latitude: latCoordinates[id][1], longitude: longCoordinates[id][1])
        midCoordinate = CLLocationCoordinate2D(latitude: latCoordinates[id][2], longitude: longCoordinates[id][2])
  }
}
