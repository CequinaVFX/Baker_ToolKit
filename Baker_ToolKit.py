##############################################################################
#                                                                            #
# Baker ToolKit															     #
# V 2.0                                                                      #
# Release January 10 2021                                                    #
#                                                                            #
# Created by Luciano Cequinel (vimeo.com/cequinavfx)                         #
# to report bugs or suggestions lucianocequinel@gmail.com                    #
#                                                                            #
##############################################################################

'''

Just write
import TrackerTools
on menu.py
and copy TrackerTools.py to .nuke folder

See ref_menu.py as reference.

'''

import nuke, operator, time


########################################
# Function to mark all tracks on Tracker 
#
def mark_all_trackers(node, t_knob_value, r_knob_value, s_knob_value):

	''' All credits to Isaac Spiegel, I stole from him! www.isaacspiegel.com '''

	knob = node['tracks']
	num_columns = 31
	col_translate = 6
	col_rotate = 7
	col_scale = 8
	count = 0
	trackers_knob_value = 'All'

	frame_range = nuke.FrameRange('%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame()))

	# Put toScript in list:
	trackers = []
	script = node['tracks'].toScript()
	trackers.append(script)  # add to list

	task = nuke.ProgressTask( 'Marking properties:' )

	# Get number of tracks from list:
	for item in trackers:
		total_tracks = item.count('track ')

	# Check ALL boxes:
	# Math = (True (1) or False (0), 31 columns * track number (0 to infinity)
	# + Translate (6), Rotate (7), or Scale (8))

	if total_tracks >= 1:

		if trackers_knob_value == 'All':

			while count <= int(total_tracks)-1:

				task.setMessage( 'Checking tracks: ' + str(count) )   
				task.setProgress( int ( float (count) / frame_range.last() * 100 ) )


				if all([t_knob_value, r_knob_value, s_knob_value]):
					knob.setValue(True, num_columns * count + col_translate)
					knob.setValue(True, num_columns * count + col_rotate)
					knob.setValue(True, num_columns * count + col_scale)

				elif not any([t_knob_value, r_knob_value, s_knob_value]):
					knob.setValue(False, num_columns * count + col_translate)
					knob.setValue(False, num_columns * count + col_rotate)
					knob.setValue(False, num_columns * count + col_scale)


				if t_knob_value is True:
					knob.setValue(True, num_columns * count + col_translate)

				elif t_knob_value is False:
					knob.setValue(False, num_columns * count + col_translate)


				if r_knob_value is True:
					knob.setValue(True, num_columns * count + col_rotate)

				elif r_knob_value is False:
					knob.setValue(False, num_columns * count + col_rotate)


				if s_knob_value is True:
					knob.setValue(True, num_columns * count + col_scale)

				elif s_knob_value is False:
					knob.setValue(False, num_columns * count + col_scale)
				
				count += 1

				time.sleep( 0.02 )
#
#
# End of mark_all_trackers function
###################################
#
#
###################################################
# Function to get the properties to check on tracks
# shortcut: alt + shift + t
#
def get_Properties():

	try:
		node = nuke.selectedNode()

		if node.Class() not in ('Tracker4'):
			nuke.message('Select a Tracker!')
			return

	except:
		nuke.message('Select a Tracker!')
		return

	z = nuke.Panel('Mark all tracks...')

	z.addBooleanCheckBox('Translate', 'True')
	z.addBooleanCheckBox('Rotate', 'True')
	z.addBooleanCheckBox('Scale', 'True')

	result = z.show()

	if result == 0:
		return

	else:
		t_knob_value = z.value('Translate')
		r_knob_value = z.value('Rotate')
		s_knob_value = z.value('Scale')

		mark_all_trackers(node, t_knob_value, r_knob_value, s_knob_value)
#
# End of get_Properties function
################################
#
#
########################################
# Function to link a Tracker into a Roto
# Shortcut: none
#
def Tk2Roto_Linked():

	# Try get the selected node
	try:
		node = nuke.selectedNode()
		if node.Class() not in ('Tracker4'):
			nuke.message('Select a Tracker!')
			return
	except:
		nuke.message('Select a Tracker!')
		return

	#Get Values from Tracker
	t = str(node.name() + '.translate')
	r = str(node.name() + '.rotate')
	s = str(node.name() + '.scale')
	c = str(node.name() + '.center')
	ref = str(node.name() + '.reference_frame')

	#Create Roto Node linked by Expression
	newRoto = nuke.createNode('Roto')
	newRoto.setName('Roto_Linked_to_' + node.name() + '_', uncollide=True)
	newRoto.setInput(0, None)

	newRoto['translate'].setExpression(t)
	newRoto['rotate'].setExpression(r)
	newRoto['scale'].setExpression(s)
	newRoto['center'].setExpression(c)


	newRoto['tile_color'].setValue( 10485759 )
	newRoto['gl_color'].setValue( 10485759 )

	newRoto.setXpos( int (node['xpos'].getValue() + 100 ) )
	newRoto.setYpos( int (node['ypos'].getValue() + 100 ) )


	tab = nuke.Tab_Knob('Reference Frame')
	newRoto.addKnob(tab)

	tk = nuke.Int_Knob('reff',"Reference Frame")
	tk.setTooltip ('Just to see the reference frame from original tracker.')
	newRoto.addKnob(tk)

	newRoto['reff'].setExpression(ref)
	newRoto['label'].setValue('Reference Frame: [value knob.reff]')
#
# End of Tk2Roto_Linked function
################################
#
#
########################################
# Function to bake a Tracker into a Roto
# Shortcut: F2
#
def Tk2Roto_Baked():

	# Try get the selected node
	try:
		node = nuke.selectedNode()
		if node.Class() not in ('Tracker4'):
			nuke.message('Select a Tracker!')
			return
	except:
		nuke.message('Select a Tracker!')
		return

	# Try to get the frame range
	try:
		frame_range = nuke.FrameRange(nuke.getInput('Frame Range', '%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame())))
	except:
		return

	#Change Transform to Match Move just to get the right infos
	orgTransform = str(node['transform'].getValue())
	node['transform'].setValue('match-move')

	newRoto = nuke.createNode('Roto')
	newRoto.setName('Roto_From_' + node.name() + '_', uncollide=True)
	newRoto.setInput(0, None)

	newRoto['translate'].setAnimated()
	newRoto['rotate'].setAnimated()
	newRoto['scale'].setAnimated()
	newRoto['center'].setAnimated()

	# Mark True all tracks
	t_knob_value = True
	r_knob_value = True
	s_knob_value = True

	mark_all_trackers(node, t_knob_value, r_knob_value, s_knob_value)

	task = nuke.ProgressTask( 'Creating %s' %(newRoto.name()) )


	for n in frame_range:

		task.setMessage( 'Baking frame... ' + str(n) )
		task.setProgress( int( float(n)/frame_range.last() * 100 ) )

		#Get Translate
		newRoto.knob( 'translate').setValueAt( node.knob( 'translate' ).getValueAt(n)[0] , n, 0)
		newRoto.knob( 'translate').setValueAt( node.knob( 'translate' ).getValueAt(n)[1] , n, 1)
		#Get Rotate
		newRoto.knob( 'rotate').setValueAt( node.knob( 'rotate' ).getValueAt(n) , n)
		#Get Scale
		newRoto.knob( 'scale').setValueAt( node.knob( 'scale' ).getValueAt(n) , n)
		#Get Center
		newRoto.knob( 'center').setValueAt( node.knob( 'center' ).getValueAt(n)[0] , n, 0)
		newRoto.knob( 'center').setValueAt( node.knob( 'center' ).getValueAt(n)[1] , n, 1)
	

	# Cosmetics 

	newRoto['tile_color'].setValue( 11045375 )
	newRoto['gl_color'].setValue( 11045375 )

	newRoto["xpos"].setValue(node["xpos"].getValue()+50)
	newRoto["ypos"].setValue(node["ypos"].getValue()+50)


	tab = nuke.Tab_Knob('Reference Frame')
	newRoto.addKnob(tab)

	tk = nuke.Int_Knob('reference_frame',"Reference Frame")
	newRoto.addKnob(tk)
	newRoto['reference_frame'].setValue(nuke.frame())

	tk = nuke.PyScript_Knob('setFrame','Set to current frame', 'nuke.thisNode()["reference_frame"].setValue(nuke.frame())')
	newRoto.addKnob(tk)

	newRoto['label'].setValue('Reference Frame: [value reference_frame]')


	# Set the expressions to take control from reference frame
	newRoto['translate'].setExpression('curve - curve(reference_frame)')
	newRoto['rotate'].setExpression('curve - curve(reference_frame)')
	newRoto['scale'].setExpression('curve - curve(reference_frame) + 1')

	newRoto.showControlPanel()

	#Change back to Original Transform
	node['transform'].setValue(orgTransform)
#
# End of Tk2Roto_Baked function
###################################
#
#
#############################################
# Function to link a tracker into a transform
# Shortcut: none
#
def Tk2Transform_Linked():

	# Try get the selected node
	try:
		node = nuke.selectedNode()
		if node.Class() not in ('Tracker4'):
			nuke.message('Select a Tracker!')
			return
	except:
		nuke.message('Select a Tracker!')
		return

	#Get Values from Tracker
	t = str(node.name() + '.translate')
	r = str(node.name() + '.rotate')
	s = str(node.name() + '.scale')
	c = str(node.name() + '.center')

	ref = str(node.name() + '.reference_frame')

	#Create Transform Node linked by Expression
	newTransform = nuke.createNode('Transform')
	newTransform.setName('Transform_Linked_to_' + node.name() + '_', uncollide=True)
	newTransform.setInput(0, None)
	newTransform.hideControlPanel()

	# Set expressions
	newTransform['translate'].setExpression(t)
	newTransform['rotate'].setExpression(r)
	newTransform['scale'].setExpression(s)
	newTransform['center'].setExpression(c)

	# Make this node different
	newTransform['tile_color'].setValue( 2868969216 )
	newTransform['gl_color'].setValue( 2868969216 )
	newTransform.setXpos( int (node['xpos'].getValue() + 100 ) )
	newTransform.setYpos( int (node['ypos'].getValue() + 100 ) )

	# Create a tab to see the reference frame from original Tracker
	tab = nuke.Tab_Knob('Tracker Info')
	newTransform.addKnob(tab)

	tk = nuke.Int_Knob('reff',"Reference Frame")
	tk.setTooltip ('Just to see the reference frame from original tracker.')
	newTransform.addKnob(tk)

	newTransform['reff'].setExpression(ref)
	newTransform['label'].setValue('Reference Frame: [value knob.reff]')
#
# End of Tk2Transform_Linked
############################
#
#
#############################################
# Function to bake a tracker into a transform
# Shortcut: F3
#
def Tk2Transform_Baked():

	# Try get the selected node
	try:
		node = nuke.selectedNode()
		if node.Class() not in ('Tracker4'):
			nuke.message('Select a Tracker!')
			return
	except:
		nuke.message('Select a Tracker!')
		return

	# Try to get the frame range
	try:
		frame_range = nuke.FrameRange(nuke.getInput('Frame Range', '%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame())))
	except:
		return

	# Change Transform to Match Move just to get the right infos
	orgTransform = str(node['transform'].getValue())
	node['transform'].setValue('match-move')

	# Mark True all tracks
	t_knob_value = True
	r_knob_value = True
	s_knob_value = True

	mark_all_trackers(node, t_knob_value, r_knob_value, s_knob_value)

	# Create new Transform
	newTransform = nuke.createNode('Transform')
	newTransform.setName('Transform_Baked_From_' + node.name() + '_')
	newTransform.setInput(0, None)
	newTransform.hideControlPanel()

	newTransform['translate'].setAnimated()
	newTransform['rotate'].setAnimated()
	newTransform['scale'].setAnimated()
	newTransform['center'].setAnimated()

	task = nuke.ProgressTask( 'Creating %s' % (newTransform.name()))


	for n in frame_range:

		task.setMessage( 'Baking frame... ' + str(n) )
		task.setProgress( int( float(n / 2 ) / frame_range.last() * 100 ) )

		#Get Translate
		newTransform.knob( 'translate' ).setValueAt( node.knob( 'translate' ).getValueAt(n)[0] , n, 0)
		newTransform.knob( 'translate' ).setValueAt( node.knob( 'translate' ).getValueAt(n)[1] , n, 1)

		#Get Rotate
		newTransform.knob( 'rotate' ).setValueAt( node.knob( 'rotate' ).getValueAt(n) , n)

		#Get Scale
		newTransform.knob( 'scale' ).setValueAt( node.knob( 'scale' ).getValueAt(n) , n)

		#Get Center
		newTransform.knob( 'center' ).setValueAt( node.knob( 'center' ).getValueAt(n)[0] , n, 0)
		newTransform.knob( 'center' ).setValueAt( node.knob( 'center' ).getValueAt(n)[1] , n, 1)


	# Make this node different 
	newTransform['tile_color'].setValue( 3506469631 )
	newTransform['gl_color'].setValue( 3506469631 )
	newTransform.setXpos( int (node['xpos'].getValue() + 100 ) )
	newTransform.setYpos( int (node['ypos'].getValue() + 100 ) )

	# Create a tab to controle the reference frame
	tab = nuke.Tab_Knob('Reference Frame')
	newTransform.addKnob(tab)

	tk = nuke.Int_Knob('reference_frame',"Reference Frame")
	newTransform.addKnob(tk)
	newTransform['reference_frame'].setValue(nuke.frame())

	tk = nuke.PyScript_Knob('setFrame',"Set to current frame", 'nuke.thisNode()["reference_frame"].setValue(nuke.frame())')
	newTransform.addKnob(tk)

	# Set the expressions to take control from reference frame
	newTransform['translate'].setExpression('curve - curve(reference_frame)')
	newTransform['rotate'].setExpression('curve - curve(reference_frame)')
	newTransform['scale'].setExpression('curve - curve(reference_frame) + 1')

	ref = node['reference_frame'].getValue()
	newTransform['label'].setValue('Reference Frame: [value reference_frame]')

	#Change back to Original Transform
	node['transform'].setValue(orgTransform)
#
# End ofTk2Transform_Baked function
###################################
#
#
###############################
# Bake a CornerPin to a Tracker
# Shortcut: shift + c
#
def CPin2Tracker():

	# Try get the selected node
	try:
		node = nuke.selectedNode()
		if node.Class() not in ('CornerPin2D'):
			nuke.message('Select a CornerPin!')
			return
	except:
		nuke.message('Select a CornerPin!')
		return

	# Try to get the frame range
	try:
		frame_range = nuke.FrameRange(nuke.getInput('Frame Range', '%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame())))
	except:
		return

	keyList = []
	numColumns = 31
	count = 1

	tracker = nuke.createNode("Tracker4")

	tracker.setName('Tracker_From_' + node.name() + '_', uncollide=True)
	tracker.setInput(0, None)
	trackerNode = tracker

	tracker.setXpos( int (node['xpos'].getValue() + 100 ) )
	tracker.setYpos( int (node['ypos'].getValue() + 100 ) )

	tracker['transform'].setValue('match-move')
	tracker['reference_frame'].setValue(nuke.frame())

	tracker['tile_color'].setValue( 2080392960 )
	tracker['gl_color'].setValue( 2080392960 )

	task = nuke.ProgressTask( 'Creating Tracker %s' % (tracker.name()) )

	for i in range(4):

		task.setMessage( 'Creating Track %d' % (i) )
		task.setProgress( int( float( i )/frame_range.last() * 100 ) )


		tracker["add_track"].execute()

		toList = []

		for n in frame_range:
			t = 'to' + str(count)

			x = node.knob(t).getValueAt(n)[0]
			y = node.knob(t).getValueAt(n)[1]

			toList.append([x, y])

		count = count + 1
		keyList.append(toList)

		time.sleep(0.1)

	knob = tracker["tracks"]

	for trk_idx, tracker in enumerate(keyList):

		#task.setMessage( 'Copying animation to Track %d' % (trk_idx) )
		#task.setProgress( int( float( trk_idx )/frame_range.last() * 100 ) )

		count = 0

		for n in frame_range: # Copy animation for each frame and tracker

			task.setMessage( 'Copying animation to Track %d' % (trk_idx) )
			task.setProgress( int( float( n )/frame_range.last() * 100 ) )

			frame = n
			x, y = tracker[count]

			knob.setValueAt(x, n, numColumns * trk_idx + 2)
			knob.setValueAt(y, n, numColumns * trk_idx + 3)

			count = count + 1

		if not frame_range.isInRange(nuke.frame()): # Remove the automatic keyframe created
			for n in range(numColumns): 
				knob.removeKeyAt(nuke.frame(), numColumns * trk_idx + n)

	# Mark True all tracks
	t_knob_value = True
	r_knob_value = True
	s_knob_value = True

	node = trackerNode

	mark_all_trackers(node, t_knob_value, r_knob_value, s_knob_value)
#
# End of CPin2Tracker function
##############################
#
#
#############################################
# Create a stabilization kit from a CornerPin
# Shortcut: alt + shift + c
#
def StabFromMocha():

	# Try get the selected node
	try:
		node = nuke.selectedNode()
		if node.Class() not in ('CornerPin2D'):
			nuke.message('Select a CornerPin!')
			return
	except:
		nuke.message('Select a CornerPin!')
		return

	# Try to get the frame range
	try:
		frame_range = nuke.FrameRange(nuke.getInput('Frame Range', '%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame())))
	except:
		return

	curFrame = nuke.frame()

	#Stabilize Node
	newStab = nuke.createNode('CornerPin2D')
	newStab.setName('Stab_Baked_From_' + node.name() + '_', uncollide=True)
	newStab.setInput(0, None)

	tab = nuke.Tab_Knob('Reference Frame')
	newStab.addKnob(tab)

	fh = nuke.Int_Knob('reference_frame',"Hold at")
	newStab.addKnob(fh)
	newStab['reference_frame'].setValue(curFrame)

	fh = nuke.PyScript_Knob('setFrame', 'Set to current frame', 'nuke.thisNode()["reference_frame"].setValue(nuke.frame())')
	newStab.addKnob(fh)


	newStab['tile_color'].setValue( 542721024 )
	newStab['gl_color'].setValue( 542721024 )
	newStab['label'].setValue('Stabilize\nRef Frame: [value knob.reference_frame]')
	newStab["xpos"].setValue(node["xpos"].getValue()+150)
	newStab["ypos"].setValue(node["ypos"].getValue()+150)
	newStab.hideControlPanel()

	newStab['to1'].setAnimated()
	newStab['to2'].setAnimated()
	newStab['to3'].setAnimated()
	newStab['to4'].setAnimated()

	newStab['from1'].setAnimated()
	newStab['from2'].setAnimated()
	newStab['from3'].setAnimated()
	newStab['from4'].setAnimated()

	newStab['to1'].setExpression('curve(knob.reference_frame)')
	newStab['to2'].setExpression('curve(knob.reference_frame)')
	newStab['to3'].setExpression('curve(knob.reference_frame)')
	newStab['to4'].setExpression('curve(knob.reference_frame)')

	#Match Move Node
	newMMove = nuke.createNode('CornerPin2D')
	newMMove.setName('MatchMove_From_' + node.name() + '_', uncollide=True)
	newMMove['invert'].setValue('True')

	newMMove['to1'].setExpression(newStab.name() + '.to1')
	newMMove['to2'].setExpression(newStab.name() + '.to2')
	newMMove['to3'].setExpression(newStab.name() + '.to3')
	newMMove['to4'].setExpression(newStab.name() + '.to4')

	newMMove['from1'].setAnimated()
	newMMove['from2'].setAnimated()
	newMMove['from3'].setAnimated()
	newMMove['from4'].setAnimated()

	newMMove.setInput(0, newStab)

	newMMove['tile_color'].setValue( 2382402559 )
	newMMove['gl_color'].setValue( 2382402559 )
	newMMove['label'].setValue('MatchMove')
	newMMove["xpos"].setValue(node["xpos"].getValue()+150)
	newMMove["ypos"].setValue(node["ypos"].getValue()+500)
	newMMove.hideControlPanel()


	#Copy animations
	task = nuke.ProgressTask( 'Creating Stabilization Kit' )
	task.setMessage( 'Creating: ' + newMMove.name() )    

	for n in frame_range:

		task.setProgress( int( float(n * 2 )/frame_range.last() * 100 ) )

		#Stabilize Node
		newStab.knob( 'to1').setValueAt( node.knob( 'to1' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'to1').setValueAt( node.knob( 'to1' ).getValueAt(n)[1] , n, 1)

		newStab.knob( 'to2').setValueAt( node.knob( 'to2' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'to2').setValueAt( node.knob( 'to2' ).getValueAt(n)[1] , n, 1)

		newStab.knob( 'to3').setValueAt( node.knob( 'to3' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'to3').setValueAt( node.knob( 'to3' ).getValueAt(n)[1] , n, 1)

		newStab.knob( 'to4').setValueAt( node.knob( 'to4' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'to4').setValueAt( node.knob( 'to4' ).getValueAt(n)[1] , n, 1)   

		newStab.knob( 'from1').setValueAt( node.knob( 'to1' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'from1').setValueAt( node.knob( 'to1' ).getValueAt(n)[1] , n, 1)

		newStab.knob( 'from2').setValueAt( node.knob( 'to2' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'from2').setValueAt( node.knob( 'to2' ).getValueAt(n)[1] , n, 1)

		newStab.knob( 'from3').setValueAt( node.knob( 'to3' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'from3').setValueAt( node.knob( 'to3' ).getValueAt(n)[1] , n, 1)

		newStab.knob( 'from4').setValueAt( node.knob( 'to4' ).getValueAt(n)[0] , n, 0)
		newStab.knob( 'from4').setValueAt( node.knob( 'to4' ).getValueAt(n)[1] , n, 1)

		#Match Move Node
		newMMove.knob( 'from1').setValueAt( node.knob( 'to1' ).getValueAt(n)[0] , n, 0)
		newMMove.knob( 'from1').setValueAt( node.knob( 'to1' ).getValueAt(n)[1] , n, 1)

		newMMove.knob( 'from2').setValueAt( node.knob( 'to2' ).getValueAt(n)[0] , n, 0)
		newMMove.knob( 'from2').setValueAt( node.knob( 'to2' ).getValueAt(n)[1] , n, 1)

		newMMove.knob( 'from3').setValueAt( node.knob( 'to3' ).getValueAt(n)[0] , n, 0)
		newMMove.knob( 'from3').setValueAt( node.knob( 'to3' ).getValueAt(n)[1] , n, 1)

		newMMove.knob( 'from4').setValueAt( node.knob( 'to4' ).getValueAt(n)[0] , n, 0)
		newMMove.knob( 'from4').setValueAt( node.knob( 'to4' ).getValueAt(n)[1] , n, 1)



	#Create Backdrop
	newStab['selected'].setValue('True')
	newMMove['selected'].setValue('True')

	selNodes = nuke.selectedNodes()

	positions = [(i.xpos(), i.ypos()) for i in selNodes]
	xPos = sorted(positions, key = operator.itemgetter(0))
	yPos = sorted(positions, key = operator.itemgetter(1))
	xMinMaxPos = (xPos[0][0], xPos[-1:][0][0])
	yMinMaxPos = (yPos[0][1], yPos[-1:][0][1])

	nuke.nodes.BackdropNode(xpos = xMinMaxPos[0]-100, bdwidth = xMinMaxPos[1]-xMinMaxPos[0]+300, ypos = yMinMaxPos[0]-100, bdheight = yMinMaxPos[1]-yMinMaxPos[0]+200, label = '<center>Stabilization Setup', note_font = 'Verdana bold', note_font_size = 42, tile_color = 2637311)
#
# End of StabFromMocha function
###############################
#
#
# Add a Toolbar menu and assign a shortcut
toolbar = nuke.menu('Nodes')
cqnTools = toolbar.addMenu('CQNTools', 'Modify.png')

cqnTools.addCommand('Link Tracker to Roto', 'Baker_ToolKit.Tk2Roto_Linked()', icon='Roto.png')
cqnTools.addCommand('Bake Tracker to Roto', 'Baker_ToolKit.Tk2Roto_Baked()', 'F2', icon='Roto.png')
cqnTools.addSeparator()
cqnTools.addCommand('Link Tracker to Transform', 'Baker_ToolKit.Tk2Transform_Linked()', icon='Roto.png')
cqnTools.addCommand('Bake Tracker to Transform', 'Baker_ToolKit.Tk2Transform_Baked()', 'F3', icon='Roto.png')
cqnTools.addSeparator()
cqnTools.addCommand('Bake CornerPin to Tracker', 'Baker_ToolKit.CPin2Tracker()', 'shift+c', icon='CornerPin.png')
cqnTools.addSeparator()
cqnTools.addCommand('Stab kit from Mocha', 'Baker_ToolKit.StabFromMocha()', 'alt+c', icon='CornerPin.png')
cqnTools.addSeparator()
cqnTools.addCommand('MarkAll', 'Baker_ToolKit.get_Properties()', 'alt+shift+c', icon='Tracker.png')