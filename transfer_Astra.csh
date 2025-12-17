#!/bin/csh
setenv PATH $PATH\:/opt/local/bin\:/opt/local/sbin\:/usr/local/bin\:/usr/bin\:/bin\:/usr/sbin\:/sbin\:/opt/X11/bin\:/Library/TeX/texbin

# Telescope name (options are Io, Europa, Ganymede, Callisto)
set telescope_name="Callisto"

# Path to the directory at Windows control PC where raw data are stored
set acp_control_pc_path="//speculoos:c0ntrolPC-04@172.16.0.202/Documents/astra/images/"

# Mounting point of the Windows control PC directory on the Hub
set acp_local_path="~/ESO_data_transfer/Callisto_Astra/Astra_mount"
#set acp_local_path="~/ESO_data_transfer/Callisto_Astra/Astra_mount_test"

# Data folder on the Hub for temporary data storage (work directory)
set data_dir="~/ESO_data_transfer/Callisto_Astra/workdir"

# Log folder on the Hub
set log_dir="~/ESO_data_transfer/Callisto_Astra/Logs"

# Folder on the Hub where ESO will grab the formatted data
set eso_dir="/home/eso/data_transfer/callisto"
#set eso_dir="~/ESO_data_transfer/Callisto_Astra/test"

# Folder on Cambridge server where to write the global log file
set appcg_path="speculoos@appcs.ra.phy.cam.ac.uk:/appct/data/SPECULOOSPipeline/Observations/Callisto/."

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
        ls $acp_local_path/$date/*fits
        set listsci=$data_dir/$date/filessci.dat
	    ls $acp_local_path/$date/*fits > $listsci
        set countsci=`wc -l < "$listsci"`
	    echo ""
    	
	    echo "Copying the images to the Hub"
	    cp $acp_local_path/$date/*fits $data_dir/$date/
	    echo ""
	
        # Making a list of the images copied to the Hub
        set filelist=$data_dir/$date/infiles.dat
        echo " Making a list of the images copied to the Hub (infiles.dat)"
        ls $data_dir/$date/*fits > $filelist
        set countcopy=`wc -l < "$filelist"`
        set diffcopy=`expr $countsci - $countcopy`
        if ($diffcopy != 0) then
            echo " Some files were not copied properly to the Hub "
            python ~/ESO_data_transfer/Callisto_Astra/mail_alert.py $telescope_name $diffcopy
        else
            echo " All files were copied properly to the Hub "
        endif
        echo ""

	    echo "Running astrometry.py..."
            python ~/ESO_data_transfer/Callisto_Astra/astrometry_spirit.py $filelist
	    #python ~/ESO_data_transfer/Callisto_Astra/astrometry.py $filelist
	    echo ""

	    echo " Making a list of the solved images (infiles_solved.dat)"
	    set filelist2=$data_dir/$date/infiles_solved.dat
	    ls $data_dir/$date/*fits > $filelist2
	    echo ""

	    echo "Running headerfix.py..."
	    python ~/ESO_data_transfer/Callisto_Astra/headerfix.py $filelist2 $telescope_name
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
	    ls $data_dir/$date/SPECULOOS*fits | xargs -n 1 basename > $filelist3
	    echo ""

	    echo " Logging the number of transferred files into the global log file ($log_dir/transfer_log.txt) "
	    set logfile=$log_dir/transfer_log.txt
	    set count=`wc -l < "$filelist3"`
	    echo $date $count >> $logfile

        echo " Copying the global log file to the Cambridge server "
        sshpass -p 'eij7iaXi' scp $logfile $appcg_path
	
	    echo " Transferring the files to ESO directory "
	    mv $data_dir/$date/SPECULOOS*fits $eso_dir/.
	    echo ""

	    echo " Making a list of the non-transferred files if any (list in the $log_dir/$date folder) "
	    set filelist4=$log_dir/$date/non_transferred
	    ls $data_dir/$date/*fits | xargs -n 1 basename > $filelist4
	    set num_bad_files=`wc -l < "$filelist4"`
	    if ($num_bad_files != 0) then
	        python ~/ESO_data_transfer/Callisto_Astra/mail_alert.py $telescope_name $num_bad_files
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
        ls $acp_local_path/$date/*fits
        set listsci=$data_dir/$date/filessci.dat
        ls $acp_local_path/$date/*fits > $listsci
        set countsci=`wc -l < "$listsci"`
        echo ""
        
        echo "Copying the images to the Hub"
        cp $acp_local_path/$date/*fits $data_dir/$date/
        echo ""
    
        # Making a list of the images copied to the Hub
        set filelist=$data_dir/$date/infiles.dat
        echo " Making a list of the images copied to the Hub (infiles.dat)"
        ls $data_dir/$date/*fits > $filelist
        set countcopy=`wc -l < "$filelist"`
        set diffcopy=`expr $countsci - $countcopy`
        if ($diffcopy != 0) then
            echo " Some files were not copied properly to the Hub "
            python ~/ESO_data_transfer/Callisto_Astra/mail_alert.py $telescope_name $diffcopy
        else
            echo " All files were copied properly to the Hub "
        endif
        echo ""

	    echo "Running astrometry.py..."
	    python ~/ESO_data_transfer/Callisto_Astra/astrometry.py $filelist
	    echo ""

	    echo " Making a list of the solved images (infiles_solved.dat)"
	    set filelist2=$data_dir/$date/infiles_solved.dat
	    ls $data_dir/$date/*fits > $filelist2
	    echo ""

	    echo "Running headerfix.py..."
	    python ~/ESO_data_transfer/Callisto_Astra/headerfix.py $filelist2 $telescope_name
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
	    ls $data_dir/$date/SPECULOOS*fits | xargs -n 1 basename > $filelist3
	    echo ""

	    echo " Logging the number of transferred files into the global log file ($log_dir/transfer_log.txt) "
	    set logfile=$log_dir/transfer_log.txt
	    set count=`wc -l < "$filelist3"`
	    echo $date $count >> $logfile

        echo " Copying the global log file to the Cambridge server "
        #sshpass -p 'eij7iaXi' scp $logfile $appcg_path

	    echo " Transferring the files to ESO directory "
	    mv $data_dir/$date/SPECULOOS*fits $eso_dir/.
	    echo ""

	    echo " Making a list of the non-transferred files if any (list in the $log_dir/$date folder) "
	    set filelist4=$log_dir/$date/non_transferred
	    ls $data_dir/$date/*fits | xargs -n 1 basename > $filelist4
	    set num_bad_files=`wc -l < "$filelist4"`
	    if ($num_bad_files != 0) then
		    python ~/ESO_data_transfer/Callisto_Astra/mail_alert.py $telescope_name $num_bad_files
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


