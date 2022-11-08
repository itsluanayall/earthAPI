def compute_NDVI(band_NIR, band_red):
    return (band_NIR - band_red) / (band_NIR + band_red)