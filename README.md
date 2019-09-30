# Pull Request Tool

This hack allows you to list and fetch pull requests of your GitHub repos. Fetching creates a local branch named ```pr_<id>``` for you to test the PR on.

```
% ~/github/opendps (master) $ pr.py -l
     jimmyw   46   Redesign of main view, to support both max current and max voltage.
      tzarc   42   Zero-out DAC values when powering off.
     Spudmn   39   Version 1.00 dpsctl_GUI
     Spudmn   38   Can now build OpenDPS emulator on windows using MinGW
   Cabalist    5   Python cleanup and Py3 compatibility

% ~/github/opendps (master) $ pr.py -c 46
% ~/github/opendps (pr_46) $ 

% ~/github/opendps (master) $ pr.py -v 46
   <<opens PR in browser>>
```

This was a quick hack and may or may not work for you :)
