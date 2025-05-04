#!/usr/bin/env nextflow

// Using DSL-2
nextflow.enable.dsl=2

// All of the default parameters are being set in `nextflow.config`
params.ome_dir = "${params.wf_dir}/OMETIFF"
params.seg_dir = "${params.wf_dir}/SEGMASKS"
params.output_dir = "${params.wf_dir}/QUPATH"

// Build Input List of Batches
Channel.fromPath("${params.seg_dir}/*WholeCellMask.tiff") 
			.ifEmpty { error "No DeepCell SegMasks in ${params.seg_dir}" }
			.set { segMasks }


// -------------------------------------- //
// Function which prints help message text
def helpMessage() {
    log.info"""
Usage:

nextflow run main.nf <ARGUMENTS>

Required Arguments:

  Input Data:
  --wf_dir        Folder containing 2 Folders 'OMETIFF/' *.ome.tiff files, already segmented, with masks in 'SEGMASK/'
 
    """.stripIndent()
}
// Process to identify the maximum integer value in each TIFF file
process identifyMaxValue {
    input:
    path tiffFilePath

    output:
    tuple(path(tiffFilePath), path("pixleSplitOut_*.csv"))

	script:
    template 'splitout_pixel_series.py'

   
}
// Process to parallelize quantification for every 100 pixel value ranges
process quantifyPixelsToPolygons {
    input:
    tuple path(tiffFilePath), val(rowValues)
    
    output:
    tuple(path(tiffFilePath), path("polygons_*.geojson"))
    
    script:
	template 'generate_polygons.py'
}




			
			

// Main workflow
workflow {
    // Show help message if the user specifies the --help flag at runtime
    // or if any required params are not provided
    if ( params.help || params.ome_dir == false ){
        // Invoke the function above which prints the help message
        helpMessage()
        // Exit out and do not run anything else
        exit 1
    } else {
    
    	//segMasks.view()
    	mxByImage = identifyMaxValue(segMasks)
    	//mxByImage.view()

    	
		// Use Channel.splitCsv to split each CSV into rows and pair with the corresponding image
		scatterChannel = mxByImage
		.map { imageFile, csvFile ->
		    // Split the CSV into rows with header and map to the desired format
		    Channel
		        .fromPath(csvFile) // Convert csvFile to a path object
		        .splitCsv(header: true) // Split CSV into rows with headers
		        .map { row -> path(imageFile), row.start.toInteger(), row.end.toInteger() }
		        
		}.count().view()
		
//scatterChannel.take(10).subscribe { item ->
//    println(item)
//}

					
		//geojsonSplits = quantifyPixelsToPolygons(scatterChannel)
    
    }
}


