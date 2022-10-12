def getfield_mat(model):
    # data = scio.loadmat(matfile, simplify_cells=False)
    str_set = str(model.dtype)[2:-2].split(", 'O'), (")
    fieldname = []
    for i in range(0, len(str_set)-1):
        fieldname.append(str_set[i][1:-1])
    lastone,b,c = str_set[-1].partition("', '") 
    fieldname.append(lastone[1:])
    return fieldname

if __name__ == "__main__":
    matfile = './soc/280Ahmodel.mat'
    import scipy.io as scio
    model = scio.loadmat(matfile)['model']
    fieldname = getfield_mat(model)
    print(fieldname)