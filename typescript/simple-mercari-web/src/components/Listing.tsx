import { useRef, useState } from 'react';
import { postItem } from '~/api';

interface Prop {
  setReload: (value: boolean) => void; 
}

type FormDataType = {
  name: string;
  category: string;
  image: string | File;
};


export const Listing = ({ setReload }: Prop) => {
  const initialState: FormDataType = {
    name: '',
    category: '',
    image: '',
  };

  const [values, setValues] = useState<FormDataType>(initialState);
  const uploadImageRef = useRef<HTMLInputElement>(null);

  const onValueChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValues((prev) => ({
      ...prev,
      [event.target.name]: event.target.value,
    }));
  };

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setValues((prev) => ({
      ...prev,
      [event.target.name]: event.target.files ? event.target.files[0] : '',
    }));
  };

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const REQUIRED_FIELDS = ['name', 'image'];
    const missingFields = REQUIRED_FIELDS.filter((field) => !values[field as keyof FormDataType]);

    if (missingFields.length > 0) {
      alert(`Missing fields: ${missingFields.join(', ')}`);
      return;
    }

    try {
      await postItem({
        name: values.name,
        category: values.category,
        image: values.image,
      });
      alert('Item listed successfully');
      
      setReload(true); 
      setValues(initialState);
      if (uploadImageRef.current) {
        uploadImageRef.current.value = '';
      }
    } catch (error) {
      console.error('POST error:', error);
      alert('Failed to list this item');
    }
  };

  return (
    <div className="Listing">
      <form onSubmit={onSubmit}>
        <div className="form-container">
          <input
            type="text"
            name="name"
            id="name"
            placeholder="Name"
            onChange={onValueChange}
            required
            value={values.name}
          />
          <input
            type="text"
            name="category"
            id="category"
            placeholder="Category"
            onChange={onValueChange}
            value={values.category}
          />
          <input
            type="file"
            name="image"
            id="image"
            onChange={onFileChange}
            required
            ref={uploadImageRef}
          />
          <button type="submit">Add this item</button>
        </div>
      </form>
    </div>
  );
};