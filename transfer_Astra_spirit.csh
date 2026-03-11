#!/bin/csh
setenv PATH $PATH\:/opt/local/bin\:/opt/local/sbin\:/usr/local/bin\:/usr/bin\:/bin\:/usr/sbin\:/sbin\:/opt/X11/bin\:/Library/TeX/texbin

# Load credentials from external file
if (-f ~/.credentials.csh) then
    source ~/.credentials.csh
else if (-f `dirname $0`/.credentials.csh) then
    source `dirname $0`/.credentials.csh
else
    echo "ERROR: Credentials file not found!"
    echo "Please copy .credentials.csh.example to .credentials.csh and configure it."
    echo "Expected locations: ~/.credentials.csh or script_directory/.credentials.csh"
    exit 1
endif

# Validate required environment variables
if (! $?TELESCOPE_NAME) then
    echo "ERROR: TELESCOPE_NAME not set in credentials file!"
    exit 1
endif

# Unset Python environment variables to avoid conflicts with conda
unsetenv PYTHONHOME
unsetenv PYTHONPATH

# Activate conda environment if available
if ( -f /home/speculoos/Programs/anaconda2/etc/profile.d/conda.csh ) then
    source /home/speculoos/Programs/anaconda2/etc/profile.d/conda.csh
    conda activate speculoos_py3
    echo "Activated conda environment: speculoos_py3"
    echo ""
else
    echo "Warning: Conda not found at /home/speculoos/Programs/anaconda2"
    echo "Using system python3 - ensure packages are installed"
    echo ""
endif

# Set variables from environment (loaded from .credentials.csh)
set telescope_name="${TELESCOPE_NAME}"
set acp_control_pc_path="//${CONTROL_PC_USER}:${CONTROL_PC_PASSWORD}@${CONTROL_PC_IP}${CONTROL_PC_PATH}"
set acp_local_path="${ACP_LOCAL_PATH}"
set data_dir="${DATA_DIR}"
set log_dir="${LOG_DIR}"
set eso_dir="${ESO_DIR}"
set appcg_path="${CAMBRIDGE_SERVER_USER}@${CAMBRIDGE_SERVER_HOST}:${CAMBRIDGE_SERVER_PATH}"

echo ""
echo "********************************************"
echo "Data transfer for $telescope_name"
echo "Data formatting and transfer to ESO database"
echo "********************************************"
echo ""
echo "Start: `date`"
echo ""


echo "Mounting Astra directory in $acp_local_path"
mount $acp_local_path
echo ""

# Date of start of the night can be current date - 1 or an argument of the command
# In format YYYYMMDD
# Optional second argument: program ID (e.g., "61.A-1234(A)")
if ("$1" == "") then
    set date="`date --date=yesterday +%Y%m%d`"
    set prog_id=""
    echo "Night transferred (date of the start of the night):" "$date"
    echo ""

    # Checking if a folder with the data for that night exists
    if (-e $acp_local_path/$date) then

	    echo "Folder $acp_local_path/$date exists"
	    echo ""

        # Creating temporary directory in the Hub work directory
        if  (! -e $data_dir/$date) then
            echo "Making $data_dir/$date folder"
            mkdir $data_dir/$date
            echo ""
        else
            echo "Folder $data_dir/$date already exists"
            echo "Clearing it"
            rm -r $data_dir/$date/*
        echo ""
        endif
    
	    echo "The images are:"
        find $acp_local_path/$date -maxdepth 1 -name "*fits" -type f
        set listsci=$data_dir/$date/filessci.dat
	    find $acp_local_path/$date -maxdepth 1 -name "*fits" -type f > $listsci
        set countsci=`wc -l < "$listsci"`
	    echo ""
    	
	    echo "Copying the images to the Hub"
	    find $acp_local_path/$date -maxdepth 1 -name "*fits" -type f -exec cp {} $data_dir/$date/ \;
	    echo ""
	
        # Making a list of the images copied to the Hub
        set filelist=$data_dir/$date/infiles.dat
        echo " Making a list of the images copied to the Hub (infiles.dat)"
        find $data_dir/$date -maxdepth 1 -name "*fits" -type f > $filelist
        set countcopy=`wc -l < "$filelist"`
        set diffcopy=`expr $countsci - $countcopy`
        if ($diffcopy != 0) then
            echo " Some files were not copied properly to the Hub "
            python3 ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $diffcopy
        else
            echo " All files were copied properly to the Hub "
        endif
        echo ""

	echo "Running astrometry.py..."
            python3 ${PYTHON_SCRIPTS_PATH}/astrometry_spirit.py $filelist
	    #python3 ~/ESO_data_transfer/Callisto_Astra/astrometry.py $filelist
	    echo ""

	    echo " Making a list of the solved images (infiles_solved.dat)"
	    set filelist2=$data_dir/$date/infiles_solved.dat
	    find $data_dir/$date -maxdepth 1 -name "*fits" -type f > $filelist2
	    echo ""

	echo "Running headerfix.py..."
	    if ("$prog_id" == "") then
		python3 ${PYTHON_SCRIPTS_PATH}/headerfix.py $filelist2 $telescope_name
	    else
		python3 ${PYTHON_SCRIPTS_PATH}/headerfix.py $filelist2 $telescope_name "$prog_id"
	    endif
	    echo ""

	echo "Running create_datacubes.py..."
	    python3 ${PYTHON_SCRIPTS_PATH}/create_datacubes.py $data_dir/$date $data_dir/$date
	    echo ""

        if  (! -e $log_dir/$date) then
            echo "Making $log_dir/$date folder"
            mkdir $log_dir/$date
            echo ""
        else
            echo "Folder $log_dir/$date already exists"
            echo "Clearing it"
            rm -r $log_dir/$date
            mkdir $log_dir/$date
            echo ""
        endif

	    echo " Moving datacubes to ESO directory "
	    set cubes_expected=$log_dir/$date/cubes_created
	    find $data_dir/$date -maxdepth 1 \( -name "SPECU*_S_*.fits" -o -name "SPECU*_C_*.fits" \) -type f -exec basename {} \; > $cubes_expected
	    find $data_dir/$date -maxdepth 1 \( -name "SPECU*_S_*.fits" -o -name "SPECU*_C_*.fits" \) | xargs -IFILE mv FILE $eso_dir/.
	    echo ""

	    echo " Making a list of the transferred datacubes (list in the $log_dir/$date folder)"
	    set filelist3=$log_dir/$date/transferred
	    set filelist4=$log_dir/$date/non_transferred
	    # Check each expected cube by name directly in $eso_dir (mv preserves mtime so -newer is unreliable)
	    rm -f $filelist3 $filelist4
	    touch $filelist3 $filelist4
	    foreach cube (`cat $cubes_expected`)
		if (-f $eso_dir/$cube) then
		    echo $cube >> $filelist3
		else
		    echo $cube >> $filelist4
		endif
	    end
	    echo ""

	    echo " Checking for datacubes that failed to transfer "
	    set num_bad_files=`wc -l < "$filelist4"`
	    if ($num_bad_files != 0) then
	        echo " Warning: $num_bad_files datacube(s) failed to transfer to ESO "
	        python3 ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $num_bad_files
	    else
	        echo " All datacubes transferred successfully to ESO "
	    endif
	    echo ""

	    echo " Logging the number of transferred datacubes into the global log file ($log_dir/transfer_log.txt) "
	    set logfile=$log_dir/transfer_log.txt
	    set count=`wc -l < "$filelist3"`
	    echo $date $count >> $logfile

        echo " Copying the global log file to the Cambridge server "
        sshpass -p "${CAMBRIDGE_SERVER_PASSWORD}" scp $logfile $appcg_path

	    echo " Deleting the data folder on the Hub for temporary data storage"
	    rm -r $data_dir/$date
	    echo ""

    else
	    echo "Folder $acp_local_path/$date does not exist"
	    echo ""
        set logfile=$log_dir/transfer_log.txt
        set count=0
        echo $date $count >> $logfile
    endif

else
    set DATES="$1"
    if ("$2" == "") then
        set prog_id=""
    else
        set prog_id="$2"
    endif
    foreach date ($DATES)
	echo $date
	echo "Night transferred (date of the start of the night):" "$date"
	echo ""
	
	# Checking if a folder with the data for that night exists
	if (-e $acp_local_path/$date) then

	    echo "Folder $acp_local_path/$date exists"
	    echo ""

        # Creating temporary directory in the Hub work directory
        if  (! -e $data_dir/$date) then
            echo "Making $data_dir/$date folder"
            mkdir $data_dir/$date
            echo ""
        else
            echo "Folder $data_dir/$date already exists"
            echo "Clearing it"
            rm -r $data_dir/$date/*
            echo ""
        endif

        echo "The images are:"
        find $acp_local_path/$date -maxdepth 1 -name "*fits" -type f
        set listsci=$data_dir/$date/filessci.dat
        find $acp_local_path/$date -maxdepth 1 -name "*fits" -type f > $listsci
        set countsci=`wc -l < "$listsci"`
        echo ""
        
        echo "Copying the images to the Hub"
        find $acp_local_path/$date -maxdepth 1 -name "*fits" -type f -exec cp {} $data_dir/$date/ \;
        echo ""
    
        # Making a list of the images copied to the Hub
        set filelist=$data_dir/$date/infiles.dat
        echo " Making a list of the images copied to the Hub (infiles.dat)"
        find $data_dir/$date -maxdepth 1 -name "*fits" -type f > $filelist
        set countcopy=`wc -l < "$filelist"`
        set diffcopy=`expr $countsci - $countcopy`
        if ($diffcopy != 0) then
            echo " Some files were not copied properly to the Hub "
            python3 ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $diffcopy
        else
            echo " All files were copied properly to the Hub "
        endif
        echo ""

	echo "Running astrometry.py..."
	    python3 ${PYTHON_SCRIPTS_PATH}/astrometry_spirit.py $filelist
	    echo " Making a list of the solved images (infiles_solved.dat)"
	    set filelist2=$data_dir/$date/infiles_solved.dat
	    find $data_dir/$date -maxdepth 1 -name "*fits" -type f > $filelist2
	    echo ""

	    echo "Running headerfix.py..."
	    if ("$prog_id" == "") then
		python3 ${PYTHON_SCRIPTS_PATH}/headerfix.py $filelist2 $telescope_name
	    else
		python3 ${PYTHON_SCRIPTS_PATH}/headerfix.py $filelist2 $telescope_name "$prog_id"
	    endif
	    echo ""

	    echo "Running create_datacubes.py..."
	    python3 ${PYTHON_SCRIPTS_PATH}/create_datacubes.py $data_dir/$date $data_dir/$date
	    echo ""

        if  (! -e $log_dir/$date) then
            echo "Making $log_dir/$date folder"
            mkdir $log_dir/$date
            echo ""
        else
            echo "Folder $log_dir/$date already exists"
            echo "Clearing it"
            rm -r $log_dir/$date
            mkdir $log_dir/$date
            echo ""
        endif

	    echo " Moving datacubes to ESO directory "
	    set cubes_expected=$log_dir/$date/cubes_created
	    find $data_dir/$date -maxdepth 1 \( -name "SPECU*_S_*.fits" -o -name "SPECU*_C_*.fits" \) -type f -exec basename {} \; > $cubes_expected
	    find $data_dir/$date -maxdepth 1 \( -name "SPECU*_S_*.fits" -o -name "SPECU*_C_*.fits" \) | xargs -IFILE mv FILE $eso_dir/.
	    echo ""

	    echo " Making a list of the transferred datacubes (list in the $log_dir/$date folder)"
	    set filelist3=$log_dir/$date/transferred
	    set filelist4=$log_dir/$date/non_transferred
	    # Check each expected cube by name directly in $eso_dir (mv preserves mtime so -newer is unreliable)
	    rm -f $filelist3 $filelist4
	    touch $filelist3 $filelist4
	    foreach cube (`cat $cubes_expected`)
		if (-f $eso_dir/$cube) then
		    echo $cube >> $filelist3
		else
		    echo $cube >> $filelist4
		endif
	    end
	    echo ""

	    echo " Checking for datacubes that failed to transfer "
	    set num_bad_files=`wc -l < "$filelist4"`
	    if ($num_bad_files != 0) then
	        echo " Warning: $num_bad_files datacube(s) failed to transfer to ESO "
	        python3 ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $num_bad_files
	    else
	        echo " All datacubes transferred successfully to ESO "
	    endif
	    echo ""

	    echo " Logging the number of transferred datacubes into the global log file ($log_dir/transfer_log.txt) "
	    set logfile=$log_dir/transfer_log.txt
	    set count=`wc -l < "$filelist3"`
	    echo $date $count >> $logfile

        echo " Copying the global log file to the Cambridge server "
        sshpass -p "${CAMBRIDGE_SERVER_PASSWORD}" scp $logfile $appcg_path

	    echo " Deleting the data folder on the Hub for temporary data storage"
	    rm -r $data_dir/$date
	    echo ""

	else
	    echo "Folder $acp_local_path/$date does not exist"
	    echo ""
        set logfile=$log_dir/transfer_log.txt
        set count=0
        echo $date $count >> $logfile
	endif
    end
endif

echo "End: `date`"
echo "Finished."
echo ""


