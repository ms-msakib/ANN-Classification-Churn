# Error Logs

A running log of every issue faced while building the ANN Classification (Customer Churn) project, how it was resolved, and what to watch out for in the future.

---

## How to add a new entry

Copy the template below, paste it at the **top** of the "Log Entries" section (newest first), and increment the ID.

```markdown
### ERR-XXX: <Short title of the issue>

- **Date:** YYYY-MM-DD
- **File / Area:** <e.g. app.py, experiments.ipynb, environment setup>
- **Status:** Resolved | Open | Workaround

**Error message:**
```
<paste the exact error / traceback here>
```

**Cause:**
<Why the error happened.>

**Resolution:**
1. <Step taken to fix it>
2. <...>

**Prevention / Notes for the future:**
- <What to check or do differently next time>
```

---

## Log Entries

### ERR-010: Merge conflict in `.gitignore` on `git pull --allow-unrelated-histories`

- **Date:** 2026-10-02
- **File / Area:** .gitignore, Git / GitHub setup
- **Status:** Resolved

**Error message:**
```
> git pull origin main --allow-unrelated-histories
Auto-merging .gitignore
CONFLICT (add/add): Merge conflict in .gitignore
Automatic merge failed; fix conflicts and then commit the result.
```

**Cause:**
The GitHub repo was created with its own `README.md` and `.gitignore` (GitHub's Python template). The local project also had a `.gitignore`. Both histories added the same file with different content, so Git couldn't merge it automatically.

**Resolution:**
1. Kept GitHub's Python `.gitignore` (it already ignores `venv/`, `.venv`, `__pycache__/`, `.ipynb_checkpoints`).
2. Added the project-specific lines it was missing: `logs/` (TensorBoard), `.vscode/`, `.DS_Store`, `Thumbs.db`.
3. `git add .gitignore`, then `git commit --no-edit` (completes the merge), then `git push -u origin main`.

**Prevention / Notes for the future:**
- When creating a GitHub repo for existing local code, **don't** tick "Add README / .gitignore / license". Then a plain `git push -u origin main` works with no pull or merge needed.
- Always add a `.gitignore` with `venv/` and `logs/` **before** the first `git add .`, so the virtual environment (hundreds of MB) is never committed.
- On a conflict, open the file, remove the `<<<<<<<`, `=======` and `>>>>>>>` markers while keeping the lines you need, then `git add` and `git commit`.

---

### ERR-009: `streamlit run app.py` fails in the terminal

- **Date:** 2026-10-02
- **File / Area:** app.py, VS Code terminal
- **Status:** Fix identified; waiting for confirmation (the exact console message wasn't captured)

**Error message:**
Not pasted. In a terminal where `venv` isn't activated, PowerShell shows:
```
streamlit : The term 'streamlit' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Investigation:**
- `app.py` runs **without any errors** inside the venv. Streamlit's `AppTest` loaded the model, the encoders and the scaler, and produced `Churn Probability: 0.02`. So the code and artifacts are fine.
- `streamlit` isn't on the system PATH. It exists only in `venv\Scripts\streamlit.exe`, and pip warned at install time that this folder isn't on PATH. If `venv` isn't activated, the terminal can't find `streamlit`, or it uses the base Miniconda Python.

**Resolution:**
1. Open a terminal in the folder that contains `app.py` (`...\annclassification\annclassification`).
2. Run the app through the venv's Python. This works with or without activation:
   ```
   .\venv\python.exe -m streamlit run app.py
   ```
   Or activate first: `conda activate .\venv`, then `streamlit run app.py`. If `conda activate` fails in PowerShell, run `conda init powershell` once and reopen the terminal.
3. The app opens at **http://localhost:8501**.

**Prevention / Notes for the future:**
- Check that the terminal prompt shows the venv before running `streamlit`, `pip` or `python`.
- `python -m <tool>` (for example `python -m streamlit`, `python -m pip`) always uses that exact Python's packages, so you avoid PATH problems.
- Run `streamlit run app.py` from the folder that contains `app.py` and the `.h5` / `.pkl` files, because the app loads them with relative paths.
- Harmless warning: `X does not have valid feature names, but OneHotEncoder was fitted with feature names`. It comes from `onehot_encoder_geo.transform([[geography]])` in app.py and doesn't affect predictions. To silence it, pass a DataFrame: `pd.DataFrame({'Geography':[geography]})`.

---

### ERR-008: TensorBoard runs but the dashboard doesn't appear inside the VS Code notebook

- **Date:** 2026-10-02
- **File / Area:** experiments.ipynb, cell `%tensorboard --logdir logs/fit`; VS Code
- **Status:** Resolved (workaround: open the dashboard in a browser)

**Error message:**
No error. The cell's output area stays blank, or shows nothing usable.

**Cause:**
After ERR-007 was fixed, TensorBoard **started correctly**: port 6006 is listening, `http://localhost:6006` returns HTTP 200, and runs `20261002-152002\train` / `validation` are found. The `%tensorboard` magic shows the dashboard by embedding `localhost:6006` inside the cell output. VS Code's notebook viewer often blocks or fails to show that embedded page, so the output looks empty.

**Resolution:**
1. Leave the `%tensorboard --logdir logs/fit` cell running.
2. Open **http://localhost:6006** in your web browser (Chrome/Edge) to see the full dashboard.
   - Or, without leaving VS Code: press `Ctrl+Shift+P`, run **Simple Browser: Show**, and enter `http://localhost:6006`.
3. If the notebook prints "Reusing TensorBoard on port 6006", that's fine: the same URL works.

**Prevention / Notes for the future:**
- In VS Code, view TensorBoard at `http://localhost:6006` instead of expecting it inside the cell.
- If the page doesn't load, check that TensorBoard is running (`netstat -ano | findstr 6006`). If it isn't, re-run the cell.
- To stop TensorBoard, restart the notebook kernel. If needed, end the `tensorboard.exe` process in Task Manager.

---

### ERR-007: `%tensorboard`: "Failed to launch TensorBoard (exited with 1)" (`No module named 'pkg_resources'`)

- **Date:** 2026-10-02
- **File / Area:** experiments.ipynb, cell `%tensorboard --logdir logs/fit`; requirements.txt
- **Status:** Resolved

**Error message:**
```
ERROR: Failed to launch TensorBoard (exited with 1).
Contents of stderr:
  File "...\venv\Lib\site-packages\tensorboard\default.py", line 30, in <module>
    import pkg_resources
ModuleNotFoundError: No module named 'pkg_resources'
```

**Cause:**
TensorBoard **2.15** imports `pkg_resources`, which used to come with `setuptools`. The venv had **setuptools 83.0.0**, and newer setuptools releases (81+) no longer include `pkg_resources`. So the TensorBoard process crashed as soon as it started. The notebook only shows the short "exited with 1" message; the real cause is in the "Contents of stderr" section below it.

**Resolution:**
1. Downgraded setuptools in the venv: `pip install "setuptools<81"` (installed 80.10.2).
2. Added `setuptools<81` to `requirements.txt` so a fresh install doesn't break again.
3. Checked: `venv\Scripts\tensorboard.exe --logdir logs/fit` now prints `Serving TensorBoard on localhost`.
4. In the notebook: **Restart** the kernel, run `%load_ext tensorboard`, then `%tensorboard --logdir logs/fit`.

**Prevention / Notes for the future:**
- With older TF/TensorBoard versions (2.15 or earlier), pin `setuptools<81`.
- When a tool "exits with 1", read the **full stderr / traceback** below the short message. The last line names the real cause.
- `ModuleNotFoundError: No module named 'pkg_resources'` usually means a new setuptools is installed alongside an old package. Fix it by pinning `setuptools<81`.

---

### ERR-006: `KeyError: "['Geography'] not found in axis"` when combining the one-hot columns

- **Date:** 2026-10-02
- **File / Area:** experiments.ipynb, cell "Combine one hot encoder columns with the original data"
- **Status:** Resolved (fix: restart the kernel and run all cells in order)

**Error message:**
```
data=pd.concat([data.drop('Geography',axis=1),geo_encoded_df],axis=1)
KeyError: "['Geography'] not found in axis"
```

**Cause:**
The cell was **run more than once**. The first run drops `Geography` and saves the result back into `data`, so the column no longer exists. A second run tries to drop it again and fails. The code is correct: running the whole notebook top to bottom in a fresh kernel works without errors. The problem is the notebook's state.

**Resolution:**
1. Click **Restart** on the notebook toolbar (this clears all variables).
2. Click **Run All**, or run the cells in order from the top, starting with `pd.read_csv(...)`.

**Prevention / Notes for the future:**
- Cells that **change a variable in place** (`data = data.drop(...)`, `data = pd.concat(...)`, `data['Gender'] = encoder.fit_transform(...)`) must run **only once** for each data load. If you need to run them again, first re-run the `pd.read_csv` cell, or restart the kernel.
- `KeyError: ... not found in axis` after a re-run almost always means the column was already dropped or renamed. Check with `data.columns`.
- If anything looks off, use **Restart + Run All** to get a clean, top-to-bottom state.

---

### ERR-005: Notebook not working after a kernel was selected in VS Code

- **Date:** 2026-10-02
- **File / Area:** experiments.ipynb, VS Code Jupyter kernel selection
- **Status:** Resolved (2026-10-02, confirmed by the user: the notebook runs on the **annclassification (venv, Python 3.11)** kernel)

**Error message:**
The kernel was selected but cells didn't run properly. No exact message was captured. Switching to the dedicated venv kernel fixed it, which confirms that a wrong or broken kernel was the cause.

**Investigation:**
- Running every code cell of `experiments.ipynb` with `venv\python.exe` (on a copy in a temp folder) finished without errors. So the **code and packages are fine**, and the problem is which kernel VS Code is using.
- `jupyter kernelspec list` showed two kernels that would break the notebook if selected:
  - **"ML Project (.venv)"** (`ml-project-venv`) points to `C:\Projects\ML Project\.venv\Scripts\python.exe`, which **doesn't exist** anymore. The kernel can't start.
  - **"Python 3 (ipykernel)"** (`python3`) runs plain `python`, which resolves to the Miniconda base (Python 3.14, no TensorFlow). Cells fail with `ModuleNotFoundError`.

**Resolution:**
1. Registered the project venv as a clearly named kernel:
   ```
   venv\python.exe -m ipykernel install --user --name annclassification-venv --display-name "annclassification (venv, Python 3.11)"
   ```
2. In VS Code, run **Developer: Reload Window**, then in the notebook choose **Select Kernel**, **Jupyter Kernel...**, and **annclassification (venv, Python 3.11)**. (**Python Environments...**, then `venv\python.exe`, also works.)
3. Check it with a cell: `import sys; print(sys.executable)`. The output must end in `annclassification\venv\python.exe`.
4. Removed the broken kernel: `jupyter kernelspec remove ml-project-venv` (done 2026-10-02).

**Prevention / Notes for the future:**
- Give every project's kernel a unique, descriptive name when registering it.
- Run `print(sys.executable)` first in any notebook to confirm which Python it is using.
- Remove kernelspecs when their environment is deleted, so broken entries don't stay in the kernel list.

---

### ERR-004: `ipykernel` missing from the new `venv`, so the notebooks can't run

- **Date:** 2026-10-02
- **File / Area:** requirements.txt, all `.ipynb` notebooks
- **Status:** Resolved

**Error message:**
None yet; this was caught before running a notebook. Without the fix, VS Code shows:
```
Running cells with 'venv (Python 3.11)' requires the ipykernel package.
```

**Cause:**
`ipykernel` wasn't listed in `requirements.txt`, so the new environment had no Jupyter kernel for VS Code to use.

**Resolution:**
1. Installed it in the environment: `pip install ipykernel` (version 7.4.0).
2. Added `ipykernel` to `requirements.txt` so future installs include it.
3. In VS Code, open the notebook, click **Select Kernel** (top right), then **Python Environments**, and choose `venv\python.exe`.

**Prevention / Notes for the future:**
- Every project that uses notebooks needs `ipykernel` in its requirements.
- After creating a new environment, select it as the kernel in each notebook before running cells.

---

### ERR-003: scikit-learn `InconsistentVersionWarning` when loading the `.pkl` files

- **Date:** 2026-10-02
- **File / Area:** scaler.pkl, label_encoder_gender.pkl, onehot_encoder_geo.pkl (used by app.py, prediction.ipynb)
- **Status:** Resolved (2026-10-02, chose option 1: pinned `scikit-learn==1.5.0`; all `.pkl` files now load with no warnings)

**Error message:**
```
InconsistentVersionWarning: Trying to unpickle estimator StandardScaler from version 1.5.0 when using version 1.9.1.
This might lead to breaking code or invalid results. Use at your own risk.
```
(The same warning appears for `LabelEncoder` and `OneHotEncoder`.)

**Cause:**
The pickled encoders and scaler were saved with scikit-learn **1.5.0**. `requirements.txt` doesn't pin a version, so the new `venv` installed the latest release, **1.9.1**. Pickled sklearn objects aren't guaranteed to work across versions.

**Resolution (choose one):**
1. **Pin the old version:** change `scikit-learn` to `scikit-learn==1.5.0` in `requirements.txt` and reinstall. **Or:**
2. **Re-generate the artifacts:** re-run the preprocessing cells in `experiments.ipynb` in the new `venv` so the `.pkl` files are saved with 1.9.1.

**Prevention / Notes for the future:**
- Pin the versions of every library whose objects get pickled (scikit-learn especially). Use `pip freeze` to record exact versions once the project works.
- Always save and load model/preprocessing artifacts with the same library versions.

---

### ERR-002: `tensorflow==2.15.0` has no build for Python 3.14

- **Date:** 2026-10-02
- **File / Area:** requirements.txt, environment setup
- **Status:** Resolved (2026-10-02, `venv` created with Python 3.11.16, all requirements installed, `pip check` clean)

**Error message:**
```
ERROR: Could not find a version that satisfies the requirement tensorflow==2.15.0 (from versions: 2.22.0rc0)
ERROR: No matching distribution found for tensorflow==2.15.0
```

**Cause:**
The active interpreter is the Miniconda base Python **3.14.7** (`C:\Miniconda3`). TensorFlow 2.15.0 only publishes wheels for Python **3.9 to 3.11**, so pip can't find a compatible version. This error was hidden behind ERR-001: it shows up once the filename typo is fixed.

**Resolution:**
1. Create a project environment with a supported Python version (run inside the project folder):
   ```
   conda create -p venv python=3.11 -y
   conda activate ./venv
   ```
2. Install the dependencies inside that environment:
   ```
   pip install -r requirements.txt
   ```

**Prevention / Notes for the future:**
- Run `python --version` before installing. Check that the version is supported by every pinned package, especially TensorFlow.
- Don't install project packages into the base Miniconda environment. Use a separate environment for each project.
- Make sure the `(venv)` prefix shows in the terminal before running pip, the notebooks, or Streamlit.

---

### ERR-001: `pip install` failed because of a typo in the requirements filename

- **Date:** 2026-10-02
- **File / Area:** environment setup (terminal command)
- **Status:** Resolved

**Error message:**
```
> pip install -r reuirements.txt
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'reuirements.txt'
```

**Cause:**
The filename was misspelled as `reuirements.txt` (missing the "q"), so pip couldn't find it. The command also fails if it is run from the outer `annclassification` folder, because `requirements.txt` is in the inner `annclassification/annclassification/` folder.

**Resolution:**
1. `cd` into the folder that contains `requirements.txt` (`C:\Projects\ML Project\annclassification\annclassification`).
2. Run the command with the correct spelling:
   ```
   pip install -r requirements.txt
   ```

**Prevention / Notes for the future:**
- Use **Tab** autocompletion for filenames in the terminal instead of typing them out.
- `[Errno 2] No such file or directory` almost always means a wrong filename or the wrong working directory. Check both with `ls` / `dir` before looking further.

---

## Quick Reference Checklist

General precautions collected from the entries above. Update this list whenever a new lesson is learned.

- [ ] Use Python 3.9 to 3.11 for this project (required by `tensorflow==2.15.0`). Check with `python --version`. (ERR-002)
- [ ] Run pip from the folder containing `requirements.txt`, and use Tab completion for filenames. (ERR-001)
- [ ] Pin the scikit-learn version so the `.pkl` files load without version warnings. (ERR-003)
- [ ] Keep `ipykernel` in `requirements.txt`, and select `venv` as each notebook's kernel. (ERR-004)
- [ ] Select the **annclassification (venv, Python 3.11)** kernel, and check it with `print(sys.executable)`. (ERR-005)
- [ ] Run each preprocessing cell once, in order. If you get a `KeyError` on a column, use **Restart + Run All**. (ERR-006)
- [ ] Keep `setuptools<81` pinned, because TensorBoard 2.15 needs `pkg_resources`. (ERR-007)
- [ ] In VS Code, view TensorBoard at `http://localhost:6006` (browser or Simple Browser), not inside the cell. (ERR-008)
- [ ] Start the app with `.\venv\python.exe -m streamlit run app.py` from the folder that contains `app.py`. (ERR-009)
- [ ] Create GitHub repos **empty** (no README or .gitignore) for existing code, and set up `.gitignore` before the first commit. (ERR-010)
- [ ] Activate the correct virtual environment before running notebooks or `streamlit run app.py`.
- [ ] Install dependencies with `pip install -r requirements.txt` after any change to it.
- [ ] Keep the saved artifacts (`model.h5`, `scaler.pkl`, `label_encoder_gender.pkl`, `onehot_encoder_geo.pkl`) in sync — re-save all of them whenever preprocessing or the model is retrained.
