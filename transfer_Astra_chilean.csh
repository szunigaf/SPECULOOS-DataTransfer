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

# -----------------------------------------------------------------------
# Chilean time usage: both date and programID are MANDATORY
# Usage: tcsh transfer_Astra_chilean.csh "YYYYMMDD [YYYYMMDD ...]" "PROG_ID"
# Example: tcsh transfer_Astra_chilean.csh "20260317 20260318" "60.A-9099(A)"
# -----------------------------------------------------------------------
if ("$1" == "") then
    echo "ERROR: Date argument is required for Chilean time transfer."
    echo "Usage: tcsh transfer_Astra_chilean.csh \"YYYYMMDD [YYYYMMDD ...]\" \"PROG_ID\""
    echo "Example: tcsh transfer_Astra_chilean.csh \"20260317\" \"60.A-9099(A)\""
    exit 1
endif

if ("$2" == "") then
    echo "ERROR: Program ID argument is required for Chilean time transfer."
    echo "Usage: tcsh transfer_Astra_chilean.csh \"YYYYMMDD [YYYYMMDD ...]\" \"PROG_ID\""
    echo "Example: tcsh transfer_Astra_chilean.csh \"20260317\" \"60.A-9099(A)\""
    exit 1
endif

set DATES="$1"
set prog_id="$2"

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
echo "Chilean time data transfer for $telescope_name"
echo "Program ID: $prog_id"
echo "Data formatting and transfer to ESO database"
echo "********************************************"
echo ""
echo "Start: `date`"
echo ""

echo "Mounting Astra directory in $acp_local_path"
mount $acp_local_path
echo ""

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
        python3 ${PYTHON_SCRIPTS_PATH}/astrometry.py $filelist
        echo ""

        echo " Making a list of the solved images (infiles_solved.dat)"
        set filelist2=$data_dir/$date/infiles_solved.dat
        find $data_dir/$date -maxdepth 1 -name "*fits" -type f > $filelist2
        echo ""

        echo "Running headerfix.py..."
        python3 ${PYTHON_SCRIPTS_PATH}/headerfix.py $filelist2 $telescope_name "$prog_id"
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

        echo " Transferring the files to ESO directory "
        find $data_dir/$date -maxdepth 1 -name "SPECULOOS*fits" -type f -exec mv {} $eso_dir/. \;
        echo ""

        echo " Making a list of the final transferred files (list in the $log_dir/$date folder)"
        set filelist3=$log_dir/$date/transferred
        find $eso_dir -maxdepth 1 -name "SPECULOOS*fits" -newer $listsci -type f -exec basename {} \; > $filelist3
        echo ""

        echo " Logging the number of transferred files into the Chilean log file ($log_dir/transfer_log_chilean.txt) "
        set logfile=$log_dir/transfer_log_chilean.txt
        set count=`wc -l < "$filelist3"`
        echo $date $count $prog_id >> $logfile

        echo " Copying the Chilean log file to the Cambridge server "
        sshpass -p "${CAMBRIDGE_SERVER_PASSWORD}" scp $logfile $appcg_path

        echo " Making a list of the non-transferred files if any (list in the $log_dir/$date folder) "
        set filelist4=$log_dir/$date/non_transferred
        find $data_dir/$date -maxdepth 1 -name "*fits" -type f -exec basename {} \; > $filelist4
        set num_bad_files=`expr $countsci - $count`
        if ($num_bad_files != 0) then
            python3 ${PYTHON_SCRIPTS_PATH}/mail_alert.py $telescope_name $num_bad_files
            echo " Some files were not transferred properly ($num_bad_files out of $countsci) "
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
        set logfile=$log_dir/transfer_log_chilean.txt
        set count=0
        echo $date $count $prog_id >> $logfile
    endif
end

echo "End: `date`"
echo "Finished."
echo ""
