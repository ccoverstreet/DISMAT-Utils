# CCO Srim Utility

This utility is used to convert the output of SRIM into an energy loss vs. depth format with sensible units.

## NEW GUI MODE!!!

- The ccosrimutil now can be run in a GUI mode (PyQt6 + Matplotlib) by not providing any command line arguments (`python ccosrimutil_gui.py`) 

## Using

### SRIM Calculation

1. Open SRIM
2. Go to **Stopping/Range Tables**
3. For the **Ion** section, choose appropriate ion species and change the highest energy to that of the desired ion beam (ex. 950 MeV Au for M-Branch GSI)
4. Create composition
    - **Important**: Make sure to keep at least 1 character **AT ALL TIMES** in any numeric field in SRIM. If a numeric field is ever empty, it will crash the program.
5. Enter correct density
    - Usually can find this info from ICSD or an approximation using Vegard's law
    - **New Feature**: This SRIM utility now recalculates depth and energy loss based on a user provided value which means the value entered into SRIM is less important/can be ignored.
6. Set stopping power units to MeV/(mg/cm^2)
7. Press **Calculate Table**
8. You should see a popup asking about output location. Press ok on this window to continue to the SRIM output
9. You should now see a window containing text with the stopping information. Copy all the text from this window into a text file.

### Using ccosrimutil

1. Download the latest version of this script
    - For convenience, you can save this script in the same directory as your SRIM output text files
2. Open the directory with this utility's Python file and your SRIM text files in a terminal

3. Run 
    - GUI Vesion
        - Run `python3 ccosrimutil_v5.py` or `python ccosrimutil_v5.py`
    - CLI Version
        - run `python3 ccosrimutil_v5.py YOURTEXTFILE.txt -p=PACKINGFRACTION -r=YOURDENSITY --save=somefilename.dat` or `python ccosrimutil_v5.py YOURTEXTFILE.txt -p=PACKINGFRACTION -r=YOURDENSITY --save=somefilename.dat`
        - Replace `YOURTEXTFILE.txt` with your SRIM text file name
        - Replace `PACKINGFRACTION ` with a value between 0.0 and 1.0
        - Replace `YOURDENSITY` with the theoretical density of your composition
        - Replace `somefilename.dat` to an output name that makes sense. This data file will have energy loss vs. depth and associated ion energy.
4. The previous command will open up 2 plotting windows with your energy loss results. 
5. All data used to generate the plots with be saved in the output file specified in the command after `--save=`. This is just a normal text file with the data stored in columns. You can use this file to plot the data however you like.
