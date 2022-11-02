//
//  TransmitterAnnotationView.swift
//  SignalMapper
//
//  Created by Connor Passe on 10/13/22.
//

import MapKit

class TransmitterAnnotationView: MKAnnotationView {
  // Required for MKAnnotationView
  required init?(coder aDecoder: NSCoder) {
    super.init(coder: aDecoder)
  }
  
  override init(annotation: MKAnnotation?, reuseIdentifier: String?) {
    super.init(annotation: annotation, reuseIdentifier: reuseIdentifier)
    image = UIImage(systemName: "antenna.radiowaves.left.and.right")!
  }
}
