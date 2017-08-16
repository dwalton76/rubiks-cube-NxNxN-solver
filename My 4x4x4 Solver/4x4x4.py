class GenerateTables:

    whole_cube = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],[4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]]
    
    size = 4
    cube = whole_cube
    
    def print_sides(first_side, side_count):
        color_names = ['W','0','G','R','B','Y']
        for line in range(size):
            for side in range(first_side, side_count + first_side):
                print(" ", end='')
                if side_count == 1 or side_count == 6:
                    print(" "*(size + 1), end='')
                for column in range(size):
                    sticker = size*line + column
                    print(color_names[cube[side][sticker]], end='')
            print()
    
    def print_cube():
        print_sides(0,1)
        print_sides(1,4)
        print_sides(5,1)
    
    print_cube()
    
    
    def inner_turn_cw(side_num):
      center_left = cube[side_num][6]
    
      cube[side_num][5] = cube[side_num][6]
      cube[side_num][6] = cube[side_num][10]
      cube[side_num][10] = cube[side_num][9]
      cube[side_num][9] = center_left
    
    
    def inner_turn_ccw(side_num):
        center_right = cube[side_num][6]
    
        cube[side_num][6] = cube[side_num][5]
        cube[side_num][5] = cube[side_num][9]
        cube[side_num][9] = cube[side_num][10]
        cube[side_num][10] = center_right
    
    def inner_turn_2(side_num):
        #should include both the inner and outer edges more work ahead :P
        center_left = cube[side_num][5]
        center_right = cube[side_num][6]
    
        cube[side_num][5] = cube[side_num][10]
        cube[side_num][10] = center_left
        cube[side_num][6] = cube[side_num][9]
        cube[side_num][9] = center_right
        
    def turn_U():
        inner_turn_cw(0)
        
        top_left_corner =  cube[0][0]
        top_left_edge = cube[0][1]
        top_right_edge = cube[0][2]
        top_right_corner = cube[0][4]
        
        cube[0][0] = cube[0][12]
        cube[0][1] = cube[0][8]
        cube[0][2] = cube[0][4]
        cube[]
             
