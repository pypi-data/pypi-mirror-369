# System and Control Task Runner

Application that performs different System and Control tasks
and demonstrates how `sysco` and `syscovis` work together.

Implementation and usage will by done in terminal, either as CLI or TUI.

As a future goal,
the explanation of the basic concepts and math should follow.

## Usage

```zsh
# to run the current main function
uv run syscorun
```

```python
# the output should look similar to that:
"""
...     # (nerd font needed for display)
"""
```

![syscorun0-1-1a1](https://github.com/silvasta/syscorun/blob/main/doc/images/syscorun-v0-1-1a1.png?raw=true)

_unfortunately I spent hours to get an html view with colors like in alacritty..._
here is how it looks on github:

<!-- <pre style="background-color: #282828; foreground-color:#f2f4f8"> -->
<pre style="background-color: #282828;"><font face = "RobotoMono Nerd Font", color=#f2f4f8 ><font color="#BE95FF">silvan</font><font color="#33B1FF">@</font><font color="#08BDBA">omen-u2504</font><font color="#EE5396">:</font><font color="#33B1FF">~/Coding/systems-and-control-python/syscorun</font><font color="#EE5396">|</font><font color="#DFDFE0">main </font><font color="#25BE6A"></font>
<font color="#33B1FF">⇒</font>  uv run syscorun
<font color="#25BE6A">2025-08-14 23:32:40.142</font> | <font color="#78A9FF"><b>DEBUG   </b></font> | <font color="#33B1FF">sysco</font>:<font color="#33B1FF">&lt;module&gt;</font>:<font color="#33B1FF">7</font> - <font color="#78A9FF"><b>Importing sysco</b></font>
<font color="#25BE6A">2025-08-14 23:32:40.185</font> | <font color="#78A9FF"><b>DEBUG   </b></font> | <font color="#33B1FF">syscovis</font>:<font color="#33B1FF">&lt;module&gt;</font>:<font color="#33B1FF">4</font> - <font color="#78A9FF"><b>Importing syscovis</b></font>
<font color="#33B1FF"><b>Initialize plotter</b></font><font color="#08BDBA"><b>...</b></font><font color="#33B1FF"><b> </b></font><font color="#25BE6A">Project root found! </font><font color="#DFDFE0"><i>set path for plots: </i></font>
<font color="#BE95FF"><i>/home/silvan/Coding/systems-and-control-python/syscorun/</i></font><font color="#C8A5FF"><i>plots</i></font>
<blink><span style="background-color:#DFDFE0"><font color="#33B1FF"><b>                            PLOTTER IS READY TO PLOT                            </b></font></span></blink>
<font color="#25BE6A">2025-08-14 23:32:40.188</font> | <font color="#78A9FF"><b>DEBUG   </b></font> | <font color="#33B1FF">syscorun</font>:<font color="#33B1FF">&lt;module&gt;</font>:<font color="#33B1FF">11</font> - <font color="#78A9FF"><b>Importing syscorun</b></font>
<span style="background-color:#33B1FF"><font color="#DFDFE0"><b>                           # Hello from sysco                                </b></font></span>
Controller loaded...
<font color="#25BE6A">2025-08-14 23:32:40.188</font> | <font color="#08BDBA"><b>WARNING </b></font> | <font color="#33B1FF">syscorun</font>:<font color="#33B1FF">main</font>:<font color="#33B1FF">27</font> - <font color="#08BDBA"><b>NotImplementedError for &lt;sysco.controller.controller.Controller object at 0x7090a4d37230&gt;</b></font>
<font color="#25BE6A">2025-08-14 23:32:40.188</font> | <font color="#08BDBA"><b>WARNING </b></font> | <font color="#33B1FF">syscorun</font>:<font color="#33B1FF">main</font>:<font color="#33B1FF">28</font> - <font color="#08BDBA"><b>Subclasses must implement get_input()</b></font>
<font color="#BE95FF">You would have been better off implementing something than sleeping in class</font><font color="#08BDBA">...</font>
save plot to /home/silvan/Coding/systems-and-control-python/syscorun/plots/task_ .jpg </font></pre>

(downloaded it should work with "RobotoMono Nerd Font" installed)
