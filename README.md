ressurect_gce
=============
A script for re-creating Google Compute Engine instances that have been terminated.


Usage
======
First dump the instance data to a file:

```
    gcutil --project stromberg-org --format json getinstance grimnir > i.json
```

Then run ressurect_instance.py:

```
    ressurect_instance.py --project stromberg-org i.json
```

This command will output a list of gcutil commands to execute in order to
ressurect the instance.

```
  gcutil --project=stromberg-org deleteinstance grimnir
  gcutil --project=stromberg-org addinstance --machine_type=f1-micro ... grimnir
```
