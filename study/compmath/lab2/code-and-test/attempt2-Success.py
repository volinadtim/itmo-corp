class Solution:
    isSolutionExists = True
    errorMessage = ""

    #
    # Complete the 'solveByCholeskyDecomposition' function below.
    #
    # The function is expected to return a DOUBLE_ARRAY.
    # The function accepts following parameters:
    #  1. INTEGER n
    #  2. 2D_DOUBLE_ARRAY matrix
    #
    def solveByCholeskyDecomposition(n, matrix):
        if not Solution.checkSymmetry(n, matrix):
            return Solution.error()
        
        for i in range(1):
            for j in range(1):
                if matrix[i][j] <= 0:
                    return Solution.error()

        L = [[0] * n for i in range(n)]
        L[0][0] = matrix[0][0] ** 0.5
        for j in range(1, n):
            L[j][0] = matrix[j][0] / L[0][0]
        for i in range(1, n):
            L[i][i] = (matrix[i][i] - sum([L[i][p] ** 2 for p in range(i)])) ** 0.5   
            
            if L[i][i] == 0:
                return Solution.error()
            for j in range(i + 1, n):
                L[j][i] = (matrix[j][i] - sum([L[i][p] * L[j][p] for p in range(i)])) / L[i][i]

        B = [matrix[i][n] for i in range(n)]

        Lt = [[L[j][i] for j in range(len(L))][::-1] for i in range(len(L[0]))][::-1]

        Y = Solution.lin(n, L, B)
        X = Solution.lin(n, Lt, Y[::-1])[::-1]

        return X + Y


    def error():
        Solution.isSolutionExists = False
        Solution.errorMessage = 'The system has no roots of equations or has an infinite set of them'
        return None


    def checkSymmetry(n, matrix):
        for i in range(n):
            for j in range(i, n):
                if matrix[i][j] != matrix[j][i]:
                    return False
        return True
    
    def lin(n, L, B):
        Y = []

        for i in range(n):
            b = B[i]
            db = 0
            for j in range(i):
                db += Y[j] * L[i][j]
            y = (b - db) / L[i][i] 
            Y.append(y)
        
        return Y