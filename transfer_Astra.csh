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


echo "Mounting ACP Astronomy directory in $acp_local_path"
mount $acp_local_path
echo ""

# Date of start of the night can be current date - 1 or an argument of the command
# In format YYYYMMDD
if ("$1" == "") then
    set date="`date --date=yesterday +%Y%m%d`"
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
            python ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $diffcopy
        else
            echo " All files were copied properly to the Hub "
        endif
        echo ""

	    echo "Running astrometry.py..."
            python ${PYTHON_SCRIPTS_PATH}/astrometry_spirit.py $filelist
	    #python ~/ESO_data_transfer/Callisto_Astra/astrometry.py $filelist
	    echo ""

	    echo " Making a list of the solved images (infiles_solved.dat)"
	    set filelist2=$data_dir/$date/infiles_solved.dat
	    find $data_dir/$date -maxdepth 1 -name "*fits" -type f > $filelist2
	    echo ""

	    echo "Running headerfix.py..."
	    python ${PYTHON_SCRIPTS_PATH}/headerfix.py $filelist2 $telescope_name
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

	    echo " Making a list of the final transferred files (list in the $log_dir/$date folder)"
	    set filelist3=$log_dir/$date/transferred
	    find $data_dir/$date -maxdepth 1 -name "SPECULOOS*fits" -type f -exec basename {} \; > $filelist3
	    echo ""

	    echo " Logging the number of transferred files into the global log file ($log_dir/transfer_log.txt) "
	    set logfile=$log_dir/transfer_log.txt
	    set count=`wc -l < "$filelist3"`
	    echo $date $count >> $logfile

        echo " Copying the global log file to the Cambridge server "
        sshpass -p "${CAMBRIDGE_SERVER_PASSWORD}" scp $logfile $appcg_path
	
	    echo " Transferring the files to ESO directory "
	    find $data_dir/$date -maxdepth 1 -name "SPECULOOS*fits" -type f -exec mv {} $eso_dir/. \;
	    echo ""

	    echo " Making a list of the non-transferred files if any (list in the $log_dir/$date folder) "
	    set filelist4=$log_dir/$date/non_transferred
	    find $data_dir/$date -maxdepth 1 -name "*fits" -type f -exec basename {} \; > $filelist4
	    set num_bad_files=`wc -l < "$filelist4"`
	    if ($num_bad_files != 0) then
	        python ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $num_bad_files
            echo " Some files were not transferred properly "
	    else
	        echo " All files were transferred properly "
	    endif
	    echo ""

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
            python ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $diffcopy
        else
            echo " All files were copied properly to the Hub "
        endif
        echo ""

	    echo "Running astrometry.py..."
	    python ${PYTHON_SCRIPTS_PATH}/astrometry.py $filelist
	    echo ""

	    echo " Making a list of the solved images (infiles_solved.dat)"
	    set filelist2=$data_dir/$date/infiles_solved.dat
	    find $data_dir/$date -maxdepth 1 -name "*fits" -type f > $filelist2
	    echo ""

	    echo "Running headerfix.py..."
	    python ${PYTHON_SCRIPTS_PATH}/headerfix.py $filelist2 $telescope_name
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

	    echo " Making a list of the final transferred files (list in the $log_dir/$date folder)"
	    set filelist3=$log_dir/$date/transferred
	    find $data_dir/$date -maxdepth 1 -name "SPECULOOS*fits" -type f -exec basename {} \; > $filelist3
	    echo ""

	    echo " Logging the number of transferred files into the global log file ($log_dir/transfer_log.txt) "
	    set logfile=$log_dir/transfer_log.txt
	    set count=`wc -l < "$filelist3"`
	    echo $date $count >> $logfile

        echo " Copying the global log file to the Cambridge server "
        #sshpass -p "${CAMBRIDGE_SERVER_PASSWORD}" scp $logfile $appcg_path

	    echo " Transferring the files to ESO directory "
	    find $data_dir/$date -maxdepth 1 -name "SPECULOOS*fits" -type f -exec mv {} $eso_dir/. \;
	    echo ""

	    echo " Making a list of the non-transferred files if any (list in the $log_dir/$date folder) "
	    set filelist4=$log_dir/$date/non_transferred
	    find $data_dir/$date -maxdepth 1 -name "*fits" -type f -exec basename {} \; > $filelist4
	    set num_bad_files=`wc -l < "$filelist4"`
	    if ($num_bad_files != 0) then
		    python ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $num_bad_files
            echo " Some files were not transferred properly "
	    else
		    echo " All files were transferred properly "
	    endif
	    echo ""

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


