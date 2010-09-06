if %1 == true  ( xcopy /Y /E /V /I /H /Q "_blender" "%AppData%\Blender Foundation\Blender\.blender" )
if %1 == false ( xcopy /Y /E /V /I /H /Q "_blender" ".blender" )
