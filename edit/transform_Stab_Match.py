import nuke, operator, time

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

        node['transform'].setValue('match-move')

        task.setMessage( 'Baking frame... ' + str(n) )
        task.setProgress( int( float(n / 2 ) / frame_range.last() * 100 ) )

        #Get Translate
        newTransform.knob( 'translate' ).setValueAt( node.knob( 'translate' ).getValueAt(n)[0] , n, 0)
        newTransform.knob( 'translate' ).setValueAt( node.knob( 'translate' ).getValueAt(n)[1] , n, 1)

        #Get Rotate
        newTransform.knob( 'rotate' ).setValueAt( node.knob( 'rotate' ).getValueAt(n) , n)

        #Get Scale
        newTransform.knob( 'scale' ).setValueAt( node.knob( 'scale' ).getValueAt(n) , n)

        node['transform'].setValue('stabilize')
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

    tk = nuke.Int_Knob('ref_frame',"Reference Frame")
    newTransform.addKnob(tk)
    newTransform['ref_frame'].setValue(nuke.frame())

    tk = nuke.PyScript_Knob('setFrame',"Set to current frame", 'nuke.thisNode()["ref_frame"].setValue(nuke.frame())')
    newTransform.addKnob(tk)

	tk = nuke.Enumeration_Knob('mode', 'mode', ['match-move', 'stabilize'])
	newTransform.addKnob(tk)


    # Set the expressions to take control from reference frame
    newTransform['translate'].setExpression('mode == 0 ? (curve - curve(ref_frame)) : (curve(ref_frame) - curve)')
    newTransform['rotate'].setExpression('mode == 0 ? (curve - curve(ref_frame)) : (curve(ref_frame) - curve)')
    newTransform['scale'].setExpression('mode == 0 ? (curve - curve(ref_frame) + 1) : (curve(ref_frame) - curve + 1)')
    newTransform['center'].setExpression('mode == 0 ? (curve - curve(ref_frame)) : (curve(ref_frame) - curve)')

    ref = node['reference_frame'].getValue()
    newTransform['label'].setValue('Reference Frame: [value ref_frame]')

    #Change back to Original Transform
    node['transform'].setValue(orgTransform)


Tk2Transform_Baked()