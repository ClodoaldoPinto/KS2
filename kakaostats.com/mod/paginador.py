from config import row_count

def paginador(linhas, page=1):
    
    paginas = 1 + int((linhas -1) / row_count)
    m = 2
    sp = [1, paginas, page / 2, (paginas - page) / 2 + page]
    sp.extend([i for i in range(page - m, page + m + 1)])
    sp = set([i for i in sp if i <= paginas and i > 0])
    return sorted(list(sp))
    