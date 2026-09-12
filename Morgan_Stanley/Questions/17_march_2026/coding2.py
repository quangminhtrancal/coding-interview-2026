
# Input: matrix = [  [1,  2,  3,  4       i -= 1 # i = 1],
                #    [5,  6,  7,  8],
                #    [9, 10, 11, 12]]
# Output: [1,2,3,4,8,12,11,10,9,5,6,7]

# row_start = 0 : to define top
# row_stop = m-1: to define bottom (m rows)
# top left to right; 
# reach last col: top to bottom; 
# :reach bottom: right to left
        # Decrease row_stop: 2 => 1
        # Increase row_start: 0 => 1
# first col: bottom to top

def output_spiral_matrix(matrix):
    
    m, n = len(matrix), len(matrix[0]) # number of rows; cols
    row_start, row_stop = 0, m-1
    col_start, col_stop = 0, n-1
    
    i, j = 0, 1 # x, y of the current position
    output = []
    
    output.append(matrix[0][0])
    
    visited = set()
    
    def is_valid(i, j):
        return 0 <= i <= m-1 and 0 <= j <= n-1 and len(output) <= m*n and (i,j ) not in visited
    
    to_continue = True
    
    while len(output) + 1< m*n:
        
        # left to right
        print(f'Before L R {i} {j} {col_stop}')
        while j <= col_stop: # col_stop = 3
            if is_valid(i, j):
                output.append(matrix[i][j])
                visited.add((i,j))
            else:
                to_continue = False
                print(f'Exception i={i} j={j} from left to right')
                print(f'Matrix {output}')
                break
                
            j += 1
        
        col_stop -= 1 # from 3 now 2
        j -= 1 # J was 4; J Now 3
        i += 1 # i = 1
        
        if not to_continue:
            break
            
        # top to bot
        while i <= row_stop: # row_stop = 2
            if is_valid(i, j):
                output.append(matrix[i][j])
                visited.add((i,j))
            else:
                to_continue = False
                print(f'Exception i={i} j={j} from top to bot')
                print(f'Matrix {output}')
                break
            i += 1
        
        row_stop -= 1 # from 2 to 1
        i -= 1 # i = 2
        j -= 1 #  j = 2
        
        if not to_continue:
            break
        
        
    
        # right to left
        while j >= col_start: # col_start = 0
            if is_valid(i, j):
                output.append(matrix[i][j])
                visited.add((i,j))
            else:
                to_continue = False
                print(f'Exception i={i} j={j} from right to left with col_start={col_start}')
                print(f'Matrix {output}')
                break
                
            j -= 1
        
        col_start += 1 # from 0 to 1
        j += 1 #  j = 0
        i -= 1
        
        if not to_continue:
            break      
        
        # bot to top
 
        while i > row_start: # row_start = 0
            if is_valid(i, j):
                output.append(matrix[i][j])
                visited.add((i,j))
            else:
                to_continue = False
                print(f'Exception i={i} j={j} from bot to top')
                print(f'Matrix {output}')
                break
            i -= 1
        
        row_start += 1 # from 0 to 1
        j += 1 #  j = 1; i = 1
        i += 1
        
        if not to_continue:
            break   
    
    

    return output
matrix = [  [1,  2,  3,  4],
            [5,  6,  7,  8],
            [9, 10, 11, 12]]
print(output_spiral_matrix(matrix))