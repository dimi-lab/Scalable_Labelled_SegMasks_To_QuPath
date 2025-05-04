#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// All of the default parameters are being set in `nextflow.config`
params.seg_file = "${params.segfile}"

// -------------------------------------- //
// Process to identify the maximum integer value in each TIFF file
process identifyMaxValue {
    input:
    path tiffFilePath

    output:
    path("pixleSplitOut_*.csv")

	script:
    template 'splitout_pixel_series.py'

   
}
// Process to parallelize quantification for every 100 pixel value ranges
process quantifyPixelsToPolygons {
	executor "slurm"
    memory "16G"
    queue "cpu-short"
    time "1:58:00"

    input:
    path(tiffFilePath)
    val(rowValues)
    
    output:
    path("poly_*.geojson")
    
    script:
	template 'generate_polygons.py'
}

process mergeAllGeoJson {
	publishDir(
        path: "${projectDir}/output",
        pattern: "merged_output.geojson",
        mode: "copy"
    )
    

	input:
	path(geojsonfiles)
	
	output:
	path("merged_output.geojson")
	
	script:
	template 'merge_geojson.py'
}


			
			

// Main workflow
workflow {
   	csvSplit = identifyMaxValue(params.seg_file)
   	parallelSplit = csvSplit.splitCsv(header: true, sep: ',').flatten() //.view()
   			
	geojsonSplits = quantifyPixelsToPolygons(params.seg_file, parallelSplit)
	
	mergeAllGeoJson(geojsonSplits.collect())
}


