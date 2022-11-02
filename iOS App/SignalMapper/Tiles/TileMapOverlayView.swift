//
//  SignalMapOverlayView.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/5/22.
//

import MapKit

class TileOverlayView: MKOverlayRenderer {
  let overlayImage: UIImage
  
  // 1
  init(overlay: MKOverlay, overlayImage: UIImage) {
    self.overlayImage = overlayImage
    super.init(overlay: overlay)
  }
  
  // 2
  override func draw(
    _ mapRect: MKMapRect,
    zoomScale: MKZoomScale,
    in context: CGContext
  ) {
    guard let imageReference = overlayImage.cgImage else { return }
    
    let rect = self.rect(for: overlay.boundingMapRect)
    context.scaleBy(x: 1.0, y: -1.0)
    context.translateBy(x: 0.0, y: -rect.size.height)
    context.draw(imageReference, in: rect)
  }
}
